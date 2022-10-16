import os
import string

import pytest

from helpers import create_unique_reference_id
from module_helpers import record_module_import_path_from_module
from function_helpers import (
    record_function_handles_from_lines, record_function_handles_from_module,
    record_function_context_and_content_from_module,
    extract_function_definition_closing_line_number
)

def test_record_all_module_file_paths():
    pass


@pytest.mark.parametrize(
    'module_path,reference_directory,expected_relative_module_import_path',
    [
        ('tests/test_helpers.py','./tests','test_helpers'),
        ('test_helpers.py','.','test_helpers'),
        (os.path.join('tests','test_functions','test_functions.py'),'tests','test_functions.test_functions'),
        (os.path.join('test_functions','test_functions.py'),os.path.join('.','test_functions'),'test_functions')
    ]
)
def test_record_module_import_path_from_module(module_path,reference_directory,expected_relative_module_import_path):
    actual_relative_module_import_path = record_module_import_path_from_module(module_path,reference_directory=reference_directory)

    assert actual_relative_module_import_path == expected_relative_module_import_path


def test_record_all_modules():
    pass


@pytest.mark.parametrize(
    'text_line, expected_function_handles',
    [
        (['    def test_function_1(x) -> str: ',],['test_function_1',]),
        (['def testFunction12(x=1,y=2,z=3) -> List[str]:','def Another100TestFunction('],['testFunction12','Another100TestFunction']),
        (['some text that does not','contain a function handle'],[])
    ]
)
def test_record_function_handles_from_lines(text_line, expected_function_handles):

    actual_function_handles = record_function_handles_from_lines(text_line)

    assert actual_function_handles == expected_function_handles


@pytest.mark.parametrize(
    'module_path,expected_record_function_handles',
    [
        (os.path.join('tests','test_functions', 'test_functions.py'), ['test_1', 'test_2', 'test_3'])
    ]
)
def test_record_function_handles_from_module(module_path,expected_record_function_handles):

    print(os.getcwd())

    assert record_function_handles_from_module(module_path) == expected_record_function_handles


def test_create_unique_function_id():

    randomly_generated_test_id = create_unique_reference_id()
    assert len(randomly_generated_test_id) == 20

    for char in randomly_generated_test_id:
        assert char in string.ascii_letters + string.digits


def test_record_all_functions_basic():
    pass

@pytest.mark.parametrize(
    'test_module_path,test_function_handle,expected_first_line_index,expected_last_line_index,expected_function_calls',
    [
        ('./tests/test_functions/test_functions.py','test_1',0,2,[]),
        ('./tests/test_functions/test_functions.py','test_2',5,9,['test_1']),
        ('./tests/test_functions/test_functions.py','test_3',12,18,['test_2','test_1'])
    ]
)
def test_record_function_context_and_content_from_module(test_module_path,test_function_handle,expected_first_line_index,expected_last_line_index,expected_function_calls):

    actual_first_line_index, actual_last_line_index, actual_function_calls = record_function_context_and_content_from_module(module_path=test_module_path,
                                                    function_handle=test_function_handle,
                                                    all_function_handles=['test_1','test_2','test_3'])

    assert actual_first_line_index == expected_first_line_index
    assert actual_last_line_index == expected_last_line_index
    assert actual_function_calls == expected_function_calls


@pytest.mark.parametrize(
    'test_module_path,test_function_first_line_index,expected_last_line_index',
    [
        ('./tests/test_functions/test_functions.py',0,2),
        ('./tests/test_functions/test_functions.py',5,9),
        ('./tests/test_functions/test_functions.py',12,18)
    ]
)
def test_extract_function_definition_closing_line_number(test_module_path,test_function_first_line_index,expected_last_line_index):

    with open(test_module_path,'r') as test_module_file:
        python_module_content = test_module_file.readlines()

    actual_last_line_index = extract_function_definition_closing_line_number(python_module_content=python_module_content,
                                                                             function_definition_first_line_index=test_function_first_line_index)

    assert actual_last_line_index == expected_last_line_index


def test_derive_normalized_function_definition_indentation_level():
    pass


def test_record_all_functions():
    pass