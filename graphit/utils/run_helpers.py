import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from graphit.settings import logger
from graphit.utils.function_helpers import record_all_functions_from_modules
from graphit.utils.graph_helpers import plot_project_graph
from graphit.utils.helpers import create_output_directory
from graphit.utils.meta_data_helpers import create_function_and_module_meta_data, get_graph_function_roots, \
    create_graph_meta_data
from graphit.utils.module_helpers import record_all_modules


def parse_graphit_arguments() -> Namespace:
    '''
    Utility function that parses the command line arguments needed to run the graphit package on a given project
    Returns:

    '''

    parser = ArgumentParser('Parse and visuazlie a given project\'s dependencies')
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
                        type=str,
                        default=['.'],
                        )
    parser.add_argument('--module-ignore-scope',
                        '-is',
                        dest='module_ignore_scope',
                        help='Set the module file paths and directories that should be ignored when looking for python'
                             ' modules for this project.',
                        nargs='+',
                        type=str,
                        default=['venv', 'tests'],
                        )
    parser.add_argument('--meta-data-export-directory',
                        '-m',
                        dest='meta_data_export_directory',
                        type=Path,
                        default=os.path.join(os.getcwd(), './output')
                        )

    command_line_args = parser.parse_args()

    logger.debug(f'Command line args: {command_line_args}')

    return command_line_args


def run_configured_graphit(command_line_args: Namespace):

    # prepare output directory
    temp_output_dir = create_output_directory(command_line_args.meta_data_export_directory)

    # create pydantic models containing meta data on all found modules
    all_modules = record_all_modules(reference_directory=command_line_args.reference_directory,
                                     scope=command_line_args.module_scope,
                                     ignore_scope=command_line_args.module_ignore_scope)

    # create pydantic models containing meta data on all found functions
    all_functions = record_all_functions_from_modules(recorded_modules=all_modules)

    # create all non-graph meta data & export
    module_meta_data, function_meta_data, function_dependency_meta_data = create_function_and_module_meta_data(all_modules,
                                                                                                               all_functions)

    module_meta_data_filepath = os.path.join(temp_output_dir,'graphit_module_meta_data.csv')
    module_meta_data.to_csv(module_meta_data_filepath, index=False)
    logger.info(f'Exported module meta data to: {module_meta_data_filepath}')

    function_meta_data_filepath = os.path.join(temp_output_dir,'graphit_function_meta_data.csv')
    function_meta_data.to_csv(function_meta_data_filepath, index=False)
    logger.info(f'Exported function meta data to: {function_meta_data_filepath}')

    function_dependency_meta_data_filepath = os.path.join(temp_output_dir,'graphit_function_dependency_meta_data.csv')
    function_dependency_meta_data.to_csv(function_dependency_meta_data_filepath, index=False)
    logger.info(f'Exported function dependency meta data to: {function_dependency_meta_data_filepath}')

    # create all graph meta data, plot flowchart & export
    graph_root_function_ids = get_graph_function_roots(function_meta_data=function_meta_data,
                                                       function_dependency_meta_data=function_dependency_meta_data)

    for graph_root_function_id in graph_root_function_ids:
        # create graph meta data for current root function node
        graph_meta_data = create_graph_meta_data(root_function_reference_id=graph_root_function_id,
                                                 module_meta_data=module_meta_data,
                                                 function_meta_data=function_meta_data,
                                                 function_dependency_meta_data=function_dependency_meta_data)

        graph_root_meta_data_filepath = os.path.join(temp_output_dir,
                                                              f'graphit_{graph_root_function_id}_graph_meta_data.csv')
        graph_meta_data.to_csv(graph_root_meta_data_filepath, index=False)
        logger.info(f'Exported graph root {graph_root_function_id} meta data to: {graph_root_meta_data_filepath}')

        # plot flow chart for current root function node and export
        full_diagram = plot_project_graph(graph_meta_data=graph_meta_data)

        graph_root_diagram_filepath = os.path.join(temp_output_dir,
                                                     f'graphit_{graph_root_function_id}_graph_root_diagram.svg')
        full_diagram.save(graph_root_diagram_filepath)
        logger.info(f'Exported graph diagram for root {graph_root_function_id} to {graph_root_diagram_filepath}.')

    logger.info('Done.')

    return