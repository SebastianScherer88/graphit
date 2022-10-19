import itertools
import os
import re
from pathlib import Path
from typing import List

from utils.model import RecordedModule
from utils.helpers import create_unique_reference_id
from settings import logger


def record_all_module_file_paths(reference_directory: Path,
                                scope: List[Path] = [],
                                ignore_scope: List[Path] = []) -> List[Path]:
    '''
    Crawls the specified content inside the reference_directory and returns all relative file paths to files that are
    best guesses of actual python files.
    :param reference_directory:
    :param scope: A list of subdirectories that should be crawled. If not specified, defaults to reference_directory
    :param ignore_scope: A list of subdirectories that should not get crawled. If not specified, will default to the
        empty list.
    :return: relevant_content: A list of file paths to best guess python modules, relative to the reference_directory
    '''

    content = os.walk(reference_directory)

    if scope:
        absolute_paths_scope = [os.path.abspath(scope_entry) for scope_entry in scope]
    else:
        absolute_paths_scope = [os.path.abspath(reference_directory)]

    logger.debug(f'Scope: {absolute_paths_scope}')

    if ignore_scope:
        absolute_paths_ignore_scope = [os.path.abspath(ignore_scope_entry) for ignore_scope_entry in ignore_scope]
    else:
        absolute_paths_ignore_scope = []

    logger.debug(f'Ignore scope: {absolute_paths_ignore_scope}')

    relevant_content = []

    for content_record in content:
        root_dir, sub_dir, files = content_record

        # only retain those files that are inside the specified directory scope
        if not any([absolute_path_scope in os.path.abspath(root_dir) for absolute_path_scope in absolute_paths_scope]):
            continue

        # also skip those files that are specifically ignored via the ignore scope
        if any([absolute_path_ignore_scope in os.path.abspath(root_dir) for absolute_path_ignore_scope in absolute_paths_ignore_scope]):
            continue

        # filter out any non- .py files
        python_module_pattern = '[a-zA-Z0-9_]{1,50}.py$'
        python_module_regex_pattern = re.compile(python_module_pattern)

        relevant_python_module_files = list(itertools.chain.from_iterable([python_module_regex_pattern.findall(file) for file in files]))

        # construct full absolute python module file path, then truncate to create relative file paths w.r.t reference
        # directory
        if relevant_python_module_files:
            relevant_absolute_file_paths = [os.path.join(root_dir,relevant_python_module_file) for relevant_python_module_file in relevant_python_module_files]
            relevant_relative_file_paths = [os.path.relpath(relevant_absolute_file_path,reference_directory) for relevant_absolute_file_path in relevant_absolute_file_paths]
            relevant_referenced_file_paths = [os.path.join(reference_directory,relevant_relative_file_path) for relevant_relative_file_path in relevant_relative_file_paths]
        else:
            relevant_referenced_file_paths = []

        relevant_content.extend(relevant_referenced_file_paths)

    return relevant_content


def record_module_import_path_from_module(module_path: Path,
                                          reference_directory: Path) -> Path:
    '''
    Returns a python module import notation format of the module's filepath relative to the reference directory

    :param module_path:
    :param reference_directory:
    :return:
    '''

    relative_module_path = os.path.relpath(module_path,start=reference_directory)

    relative_module_import_path = relative_module_path.replace(os.sep,'.').replace('.py','')

    return relative_module_import_path


def record_all_modules(reference_directory: Path,
                       scope: List[Path] = [],
                       ignore_scope: List[Path] = []) -> List[RecordedModule]:
    '''
    Helper function that creates list of RecordedModule models with the result of the crawled target directory using the
    specified scope.

    :param reference_directory:
    :param args:
    :param kwargs:
    :return:
    '''

    # record all module file paths
    recorded_module_file_paths = record_all_module_file_paths(reference_directory=reference_directory,
                                                         scope=scope,
                                                         ignore_scope=ignore_scope)

    # convert all module file paths to import paths
    recorded_import_paths = [record_module_import_path_from_module(module_path=recorded_module_file_path,reference_directory=reference_directory) for recorded_module_file_path in recorded_module_file_paths]

    # create unique reference ids for all modules
    recorded_module_ids = [create_unique_reference_id() for module in recorded_module_file_paths]

    # create all module models
    recorded_modules = [RecordedModule(
        unique_module_reference_id=module_id,
        file_path=file_path,
        import_path=import_path,
        reference_directory=reference_directory) for module_id, file_path, import_path in zip(recorded_module_ids,recorded_module_file_paths,recorded_import_paths)]

    logger.info('Recorded all modules.')
    logger.debug(f'Recorded modules: {recorded_modules}')

    return recorded_modules