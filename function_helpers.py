import re
from pathlib import Path
from typing import List, Tuple, Union

from model import RecordedModule, RecordedFunctionBasic, RecordedFunction
from settings import (
    logger,
    TAB_INDENTATION_LEVEL,
    GENERIC_FUNCTION_DEFINITION_PATTERN,
    SPECIFIC_FUNCTION_DEFINITION_PATTERN_STUMP,
    SPECIFIC_FUNCTION_DEFINITION_PATTERN_TEMPLATE,
    SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_1,
    SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_2
)

from helpers import create_unique_reference_id


def record_function_handles_from_lines(text_file: List[str]) -> List[str]:
    '''
    Identifies function handles from a list of strings assumed to be lines from a python module,
    using a very basic regex pattern

    :param text_file:
    :return:
    '''

    function_definition_regex_pattern = re.compile(GENERIC_FUNCTION_DEFINITION_PATTERN)

    function_patterns = []

    for text_line in text_file:
        function_patterns.extend(function_definition_regex_pattern.findall(text_line))

    function_handles = [function_pattern.split('def ')[1].replace('(','') for function_pattern in function_patterns]

    return function_handles


def record_function_handles_from_module(module_path: Path) -> List[str]:
    '''
    Identifies function handles from a given module as specified via its file path.
    :param module_path:
    :return:
    '''

    try:
        # read in lines of text content from module file
        with open(module_path, 'r') as python_module:
            python_module_content = python_module.readlines()
    except (FileExistsError, FileNotFoundError) as file_error:
        logger.warning(f'Error trying to read in python module {module_path}')
        raise file_error

    # identify all function handles from this module
    function_handles = record_function_handles_from_lines(text_file=python_module_content)

    return function_handles


def record_all_functions_basic(recorded_modules: List[RecordedModule]) -> List[RecordedFunctionBasic]:
    '''
    Takes a list of recorded modules and inspects them for function definitions.
    :param recorded_modules:
    :return:
    '''

    all_recorded_functions_basic = []

    for recorded_module in recorded_modules:
        recorded_function_handles = record_function_handles_from_module(module_path=recorded_module.file_path)

        recorded_functions_basic = []

        for recorded_function_handle in recorded_function_handles:
            recorded_function_basic = RecordedFunctionBasic(unique_function_reference_id=create_unique_reference_id(),
                                                            function_handle=recorded_function_handle,
                                                            source_module_reference_id=recorded_module.unique_module_reference_id,
                                                            )

            recorded_functions_basic.append(recorded_function_basic)

        all_recorded_functions_basic.extend(recorded_functions_basic)

    return all_recorded_functions_basic


def record_function_context_and_content_from_module(module_path: Path,
                                                    function_handle: str,
                                                    all_function_handles: List[str]) -> Tuple[Union[None,int],
                                                                                              Union[None,int],
                                                                                              List[str]]:
    '''
    Given a function handle, checks the text file that is loaded from the specified python module and establishes the
    starting and end line in that text file of that functions definition context. Uses that information to detect and
    list all other instances of function calls drawing from the list of known function handles.

    :param module_path:
    :param function_handle:
    :param all_function_handles:
    :return:
    '''

    try:
        # read in lines of text content from module file
        with open(module_path, 'r') as python_module:
            python_module_content = python_module.readlines()
    except (FileExistsError, FileNotFoundError) as file_error:
        logger.warning(f'Error trying to read in python module {module_path}')
        raise file_error

    # detect the beginning of the function definition context
    function_definition_regex_pattern = re.compile(SPECIFIC_FUNCTION_DEFINITION_PATTERN_STUMP + SPECIFIC_FUNCTION_DEFINITION_PATTERN_TEMPLATE.format(function_handle=function_handle))
    regex_matches_in_line = [function_definition_regex_pattern.findall(python_module_content_record) for python_module_content_record in python_module_content]
    function_definition_opening_in_line = [False if match == [] else True for match in regex_matches_in_line]

    if not any(function_definition_opening_in_line):
        return (None, None, [])

    function_definition_first_line_index = function_definition_opening_in_line.index(True)

    # detect the end of the function definition context based on return statement with one more indentation
    function_definition_last_line_index = extract_function_definition_closing_line_number(python_module_content,
                                                                                              function_definition_first_line_index)

    # list all calls to known function occurring in the function definition context we have established
    function_handles_called = []

    for function_definition_line in python_module_content[function_definition_first_line_index+1:function_definition_last_line_index]:
        for known_function_handle in all_function_handles:
            if (SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_1.format(function_handle=known_function_handle) in function_definition_line) or (SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_2.format(function_handle=known_function_handle) in function_definition_line):
                function_handles_called.append(known_function_handle)

    return function_definition_first_line_index, function_definition_last_line_index, function_handles_called


def extract_function_definition_closing_line_number(python_module_content: List[str],
                                                    function_definition_first_line_index: int) -> int:
    '''
    Function that identifies the last line of a given function's definition, provided the python module as a list of
    strings, the function name and the index of the first line of the given function's definition.
    It derives the level of indentation in the first line of the given function's definition and returns the index of
    the first line with a 'return' statement with one additional level of indentation compared to the first line.
    If it cant reasonably derive a last line for the given function's definition context, it returns the index of the
    first line.

    :param python_module_content:
    :param function_definition_first_line_index:
    :return:
    '''

    function_definition_starting_line = python_module_content[function_definition_first_line_index]

    first_line_indentation_level = derive_normalized_function_definition_indentation_level(function_definition_starting_line,
                                                                                           key_expression='def')

    logger.debug(f'First line indentation level: {first_line_indentation_level}')

    function_definition_last_line_index = function_definition_first_line_index

    for current_line_index in range(function_definition_first_line_index+1,len(python_module_content)):
        current_line = python_module_content[current_line_index]

        logger.debug(f'Scanning line for {first_line_indentation_level + TAB_INDENTATION_LEVEL}x indented return statement: {current_line}')

        if 'return' in current_line:

            logger.debug(f'Found "return" statement in line: {current_line}')

            normalized_function_definition_indentation_level = derive_normalized_function_definition_indentation_level(current_line,
                                                                                                                       key_expression='return')

            logger.debug(f'Indentation level of current line: {normalized_function_definition_indentation_level}')

            if normalized_function_definition_indentation_level == first_line_indentation_level + TAB_INDENTATION_LEVEL:

                function_definition_last_line_index = current_line_index
                break

    return function_definition_last_line_index


def derive_normalized_function_definition_indentation_level(line: str,
                                                            key_expression: str) -> int:

    indentation_stump = line.split(key_expression)[0]
    normalized_indentation_level = len(indentation_stump.replace('\t',' ' * TAB_INDENTATION_LEVEL).replace('\n',''))

    return normalized_indentation_level


def record_all_functions(recorded_functions_basic: List[RecordedFunctionBasic],
                         recorded_modules: List[RecordedModule]) -> List[RecordedFunction]:
    '''
    Takes a list of RecordedFunctionBasic and re-enters the respective source modules to scan for function definition
    scopes and function calls within that scope. Augments the incoming function meta data to create a list of
    RecordedFunction objects.

    :param recorded_functions_basic:
    :return:
    '''

    # get list of all known function handles sorted by length in descending order to avoid accidental mismatches on
    # substrings
    all_known_function_handles = [recorded_function_basic.function_handle for recorded_function_basic in recorded_functions_basic]
    all_known_function_handles.sort(key=lambda x: -len(x))

    recorded_functions = []

    for recorded_function_basic_i in recorded_functions_basic:

        # get the associated source module for this function
        for recorded_module in recorded_modules:
            if recorded_module.unique_module_reference_id == recorded_function_basic_i.source_module_reference_id:
                associated_module = recorded_module
                break

        recorded_function_scope_and_content = record_function_context_and_content_from_module(module_path=associated_module.file_path,
                                                                                              function_handle=recorded_function_basic_i.function_handle,
                                                                                              all_function_handles=all_known_function_handles)

        definition_start_line_index, definition_end_line_index, called_function_handles = recorded_function_scope_and_content

        called_functions_ids = []

        for called_function_handle in called_function_handles:
            for recorded_function_basic_j in recorded_functions_basic:
                if called_function_handle == recorded_function_basic_j.function_handle:
                    called_functions_ids.append(recorded_function_basic_j.unique_function_reference_id)

        recorded_function = RecordedFunction(**recorded_function_basic_i.dict(),
                                             definition_start_line_index=definition_start_line_index,
                                             definition_end_line_index=definition_end_line_index,
                                             ordered_function_calls=called_functions_ids)

        recorded_functions.append(recorded_function)

    return recorded_functions
