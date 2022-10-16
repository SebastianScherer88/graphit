from settings import logger
from module_helpers import record_all_modules
from function_helpers import record_all_functions_basic, record_all_functions
import pandas as pd
from argparse import ArgumentParser
from pathlib import Path
import os
from typing import List
from datetime import datetime as dt

def main():

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
                        default=['venv','tests'],
                        )
    parser.add_argument('--meta-data-export-directory',
                        '-m',
                        dest='meta_data_export_directory',
                        type=Path,
                        default=os.path.join(os.getcwd(),'output')
                        )

    command_line_args = parser.parse_args()

    logger.debug(f'Command line args: {command_line_args}')

    all_modules = record_all_modules(reference_directory=command_line_args.reference_directory,
                                     scope=command_line_args.module_scope,
                                     ignore_scope=command_line_args.module_ignore_scope)

    logger.info('Recorded all modules.')
    logger.debug(f'Recorded modules: {all_modules}')

    # export module meta data
    module_meta_data = pd.DataFrame([record.dict() for record in all_modules])
    module_meta_data_filepath = os.path.join(command_line_args.meta_data_export_directory,
                                               f'{dt.strftime(dt.now(), "%Y-%m-%d %H-%M-%S")}_graphit_module_meta_data.csv')
    module_meta_data.to_csv(module_meta_data_filepath,index=False)

    logger.info(f'Exported module meta data to: {module_meta_data_filepath}')

    all_functions_basic = record_all_functions_basic(recorded_modules=all_modules)

    logger.info('Recorded all basic function meta data.')
    logger.debug(f'Recorded functions meta data (basic): {all_functions_basic}')

    all_functions = record_all_functions(recorded_functions_basic=all_functions_basic,
                                         recorded_modules=all_modules)

    logger.info('Recorded remaining function meta data.')
    logger.debug(f'Recorded functions meta data (including scope and calls): {all_functions}')

    # export function meta data
    function_meta_data = pd.DataFrame([record.dict() for record in all_functions])
    function_meta_data_filepath = os.path.join(command_line_args.meta_data_export_directory,f'{dt.strftime(dt.now(), "%Y-%m-%d %H-%M-%S")}_graphit_function_meta_data.csv')
    function_meta_data.to_csv(function_meta_data_filepath,index=False)

    logger.info(f'Exported function meta data to: {function_meta_data_filepath}')
    logger.info(f'Done @ {dt.now()}')

    return

if __name__ == '__main__':
    main()