from typing import List
from typing import Tuple

import pandas as pd

from utils.model import RecordedModule, RecordedFunction
from settings import logger


def create_function_and_module_meta_data(all_modules: List[RecordedModule],
                                         all_functions: List[RecordedFunction]) -> Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    '''
    Helper function that consolidates the module and function meta data in the form of lists of models into 3 data
    frames:
        - module_meta_data
        - function_meta_data
        - function_dependency_meta_data
    Args:
        module_meta_data:
        function_meta_data:

    Returns:

    '''

    # module meta data
    module_meta_data = pd.DataFrame([record.dict() for record in all_modules])

    # function meta data
    function_meta_data = pd.DataFrame([record.dict() for record in all_functions])[['unique_function_reference_id',
                                                                                    'function_handle',
                                                                                    'source_module_reference_id',
                                                                                    'definition_start_line_index',
                                                                                    'definition_end_line_index',
                                                                                    'definition_start_line_offset',
                                                                                    'definition_end_line_offset',
                                                                                    'ordered_function_calls']]
    function_meta_data['n_dependency_functions'] = function_meta_data['ordered_function_calls'].apply(lambda x: len(x))
    function_meta_data.drop('ordered_function_calls',inplace=True,axis=1)

    # function meta data - with ranked function call entries
    function_dependency_meta_data_elements = []

    for function_record in all_functions:
        function_record_dict = function_record.dict()

        for function_record_calleable_index, function_record_calleable in enumerate(function_record_dict['ordered_function_calls']):
            function_meta_data_element = function_record_dict.copy()
            del function_meta_data_element['ordered_function_calls']

            function_meta_data_element['function_dependency_index'] = function_record_calleable_index
            function_meta_data_element['function_dependency_reference_id'] = function_record_calleable

            function_dependency_meta_data_elements.append(function_meta_data_element)

    function_dependency_meta_data = pd.DataFrame(function_dependency_meta_data_elements)[['unique_function_reference_id','function_dependency_reference_id','function_dependency_index']]

    logger.debug('Created all function and module meta data files for export.')

    return module_meta_data, function_meta_data, function_dependency_meta_data


def get_graph_function_roots(function_meta_data: pd.DataFrame,
                             function_dependency_meta_data: pd.DataFrame) -> List[str]:
    '''
    Utility function that identifies the function reference ids of functions that are not themselves are dependency
    for other functions, i.e. that are not called by other functions, and so would be at the top of any dependency
    graph mapping out the inter-function relations.

    Args:
        function_meta_data:
        function_dependency_meta_data:

    Returns:

    '''

    function_as_dependency_ids = function_dependency_meta_data['function_dependency_reference_id'].tolist()

    is_standalone_function_id = ~function_meta_data['unique_function_reference_id'].isin(function_as_dependency_ids)

    standalone_function_ids = function_meta_data.loc[is_standalone_function_id,'unique_function_reference_id'].tolist()

    return standalone_function_ids


def create_graph_meta_data(root_function_reference_id: str,
                           module_meta_data: pd.DataFrame,
                           function_meta_data: pd.DataFrame,
                           function_dependency_meta_data: pd.DataFrame) -> pd.DataFrame:
    '''
    Utility function that creates the meta data needed for the structure visualization of a project based on functions
    and their relationshups, as shown here: https://miro.com/app/board/uXjVPNNbgDk=/
    Args:
        root_function_reference_id:
        function_meta_data:
        function_dependency_meta_data:

    Returns:

    '''

    # create first generation
    previous_generation = pd.DataFrame(data = [('',root_function_reference_id,0,0,''),],
                                    columns = ['source_function_id','target_function_id','target_function_dependency_index','target_function_generation','target_function_graph_index'])

    all_generations = [previous_generation,]

    logger.debug(f'First generation: {previous_generation}')

    # create remaining generations
    while True:

        current_generation_list = []

        for previous_generation_record in previous_generation.itertuples():

            logger.debug(f'Previous generation\'s record: {previous_generation_record}')

            # the previous generations connection's target is the source for this generation
            current_source_function_id = previous_generation_record.target_function_id

            # get all dependencies for this source function
            current_generation_slice = function_dependency_meta_data.loc[
                function_dependency_meta_data['unique_function_reference_id'] == current_source_function_id].sort_values('function_dependency_index',ascending=True)

            if current_generation_slice.empty:
                # no dependencies recorded for this source function; move on to next element of previous generation
                continue
            else:
                # format the non-trivial dependencies of this source function
                current_generation_slice.rename(columns={'unique_function_reference_id': 'source_function_id',
                                                         'function_dependency_reference_id': 'target_function_id',
                                                         'function_dependency_index': 'target_function_dependency_index'},
                                                inplace=True)

                # generation counter simply increases by 1 compared to previous generation
                current_generation_slice['target_function_generation'] = previous_generation_record.target_function_generation + 1

                # graph index is an additional level to the previous generations target function, with the new value
                # being dependency_index + 1. the nested version number is a string type
                current_generation_slice['target_function_graph_index'] = current_generation_slice['target_function_dependency_index'].apply(lambda index: f'{previous_generation_record.target_function_graph_index}.{index+1}')

                logger.debug(f'Current generation slice: {current_generation_slice}')

                current_generation_list.append(current_generation_slice)

        if not current_generation_list:
            # no element of the previous generation had dependencies (= offsprings), so the current generation is
            # trivial
            break
        else:
            # save this generation
            current_generation = pd.concat(current_generation_list)

            logger.debug(f'Current generation after assembly: {current_generation}')

            all_generations.append(current_generation)

            # update generation placeholder variable for next iteration
            previous_generation = current_generation

    graph_meta_data = pd.concat(all_generations).sort_values('target_function_graph_index',ascending=True)

    # clean graph index: remove leading '.'
    graph_meta_data['target_function_graph_index'] = graph_meta_data['target_function_graph_index'].apply(lambda x: x[1:] if (x and x[0] == '.') else x)

    # add coordinates for plot function
    graph_meta_data['graph_plot_x_coordinate'] = graph_meta_data['target_function_generation'] # 1,2,...
    graph_meta_data['graph_plot_y_coordinate'] = range(1,len(graph_meta_data)+1) # 1,2, ..

    # merge on function information needed for the graph visualization
    graph_meta_data = graph_meta_data.merge(function_meta_data[['unique_function_reference_id','function_handle','source_module_reference_id']],
                                            how = 'left',
                                            left_on = 'target_function_id',
                                            right_on = 'unique_function_reference_id'). \
        rename(columns={'function_handle':'target_function_handle'}). \
        drop('unique_function_reference_id',axis=1)

    # merge on module information needed for the graph visualizaation
    graph_meta_data = graph_meta_data.merge(module_meta_data,
                                            how='left',
                                            left_on = 'source_module_reference_id',
                                            right_on = 'unique_module_reference_id'). \
        rename(columns={'file_path':'target_function_file_path',
                        'import_path':'target_function_module_import_path'}). \
        drop(['unique_module_reference_id','source_module_reference_id'],axis=1)

    graph_meta_data['target_function_import_path'] = graph_meta_data[['target_function_module_import_path','target_function_handle']].apply(lambda x: '.'.join(x), axis=1)
    graph_meta_data.drop(['source_function_id','target_function_id'],axis=1,inplace=True)

    return graph_meta_data