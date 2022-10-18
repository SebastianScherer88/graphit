import os
import random
from datetime import datetime as dt
from pathlib import Path
from string import ascii_letters as letters
from string import digits
from typing import List, Tuple

import pandas as pd

from model import RecordedModule, RecordedFunction
from settings import logger
from argparse import ArgumentParser, Namespace


def parse_graphit_arguments() -> Namespace:
    '''
    Utility function that parses the command line arguments needed to run the graphit package on a given project
    Returns:

    '''

    parser = ArgumentParser('Parse the graphit project dependencies')
    parser.add_argument('--reference-directory',
                        '-r',
                        dest='reference_directory',
                        help='Set the top level directory that will be the point of reference for all module file '
                             'paths.',
                        type=str,
                        default='.')
    parser.add_argument('--module-scope',
                        '-s',
                        dest='module_scope',
                        help='Set the module file paths and directories that need to be considered when looking for '
                             'python modules for this project.',
                        nargs='+',
                        type=List[Path],
                        default=['.'],
                        )
    parser.add_argument('--module-ignore-scope',
                        '-is',
                        dest='module_ignore_scope',
                        help='Set the module file paths and directories that should be ignored when looking for python'
                             ' modules for this project.',
                        nargs='+',
                        type=List[Path],
                        default=['venv', 'tests'],
                        )
    parser.add_argument('--meta-data-export-directory',
                        '-m',
                        dest='meta_data_export_directory',
                        type=Path,
                        default=os.path.join(os.getcwd(), 'output')
                        )

    command_line_args = parser.parse_args()

    logger.debug(f'Command line args: {command_line_args}')

    return command_line_args

def create_output_directory(output_directory: Path) -> Path:
    '''
    Utility function that checks the existence of the specified directory and creates a timestamped subdirectory, where
    possible.

    Args:
        output_directory:

    Returns:

    '''

    if not os.path.isdir(output_directory):
        logger.error(f'The specified output directory {output_directory} does not exist.')
    else:
        temp_output_subdir = f'{dt.strftime(dt.now(), "%Y-%m-%d %H-%M-%S")}'
        temp_output_dir = os.path.join(output_directory,temp_output_subdir)
        os.makedirs(temp_output_dir)

        logger.debug(f'Created the timestamped output directory {temp_output_dir}.')

    return temp_output_dir


def create_unique_reference_id() -> str:
    '''
    Helper function that creates a 20 character unique id from alphanumeric characters
    :return:
    '''

    return ''.join(random.choices(population=letters + digits,k=20))


def create_all_meta_data(all_modules: List[RecordedModule],
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
