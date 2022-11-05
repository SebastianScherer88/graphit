import os
import string

import pytest

from graphit.utils.helpers import create_unique_reference_id
from graphit.utils.module_helpers import record_module_import_path_from_module

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


def test_create_unique_function_id():

    randomly_generated_test_id = create_unique_reference_id()
    assert len(randomly_generated_test_id) == 20

    for char in randomly_generated_test_id:
        assert char in string.ascii_letters + string.digits


def test_record_all_functions_basic():
    pass


def test_record_all_functions():
    pass