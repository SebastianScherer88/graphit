import os
from datetime import datetime as dt

from function_helpers import record_all_functions_basic, record_all_functions
from helpers import parse_graphit_arguments, create_output_directory, create_all_meta_data
from module_helpers import record_all_modules
from settings import logger


def main():

    # get all arguments required for running graphit on the given project
    command_line_args = parse_graphit_arguments()

    # prepare output directory
    temp_output_dir = create_output_directory(command_line_args.meta_data_export_directory)

    # create pydantic models containing meta data on all found modules
    all_modules = record_all_modules(reference_directory=command_line_args.reference_directory,
                                     scope=command_line_args.module_scope,
                                     ignore_scope=command_line_args.module_ignore_scope)

    # create pydantic models containing meta data on all found functions:
    # - basic, first, then
    # - complete
    all_functions_basic = record_all_functions_basic(recorded_modules=all_modules)

    all_functions = record_all_functions(recorded_functions_basic=all_functions_basic,
                                         recorded_modules=all_modules)

    # create all meta data & export
    module_meta_data, function_meta_data, function_dependency_meta_data = create_all_meta_data(all_modules,
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

    logger.info(f'Done. @ {dt.now()}')

    return

if __name__ == '__main__':
    main()