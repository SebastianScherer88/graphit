import ast
from functools import partial
from typing import List, Dict, Union, Type, Tuple

from graphit.settings import logger
from graphit.utils.helpers import create_unique_reference_id
from graphit.utils.model import RecordedModule, RecordedFunction, RecordedClass


def record_functions_from_module(recorded_module: RecordedModule) -> List[RecordedFunction]:

    with open(recorded_module.file_path, "r") as f:
        module_ast = ast.parse(f.read(), recorded_module.file_path)

    # import pdb
    # pdb.set_trace()

    logger.debug(f'Recording functions using AST from module {recorded_module.file_path}')

    # get module level function and class definitions
    module_function_and_class_definition_nodes = get_module_level_function_and_class_definition_nodes(module_ast)

    # create RecordedFunction models from function definition nodes
    recorded_functions = convert_nodes_to_recorded_functions_and_classes(
        module_function_and_class_definition_nodes=module_function_and_class_definition_nodes,
        source_module_reference_id=recorded_module.unique_reference_id)

    return recorded_functions


def convert_nodes_to_recorded_functions_and_classes(module_function_and_class_definition_nodes: List[Type[ast.AST]],
                                                    source_module_reference_id: str) -> List[Union[RecordedFunction, RecordedClass]]:
    '''
    Walks the graphs attached to the specified function and class definition nodes at module level. Extracts the meta data needed
    to create the RecordedFunction and RecordedClass pydantic model representation of each module level function and class definition.
    Note that at this point the strings in the list type attribute ordered_function_calls are the function handles, not
    the ids, since the matching of handle and ids can only be done once all functions and classes have been recorded.

    Args:
        module_function_and_class_definition_nodes:

    Returns:

    '''

    recorded_definitions = []

    for module_function_or_class_definition_node in module_function_and_class_definition_nodes:

        # record basic data points
        definition_payload = {'unique_reference_id':create_unique_reference_id(),
                                       'function_handle':module_function_or_class_definition_node.name,
                                       'source_module_reference_id':source_module_reference_id}

        # record definition start & finish, and all (nested) - even of locally defined ones - function calls made inside
        # this definition
        definition_payload.update(
            {'definition_start_line_index':module_function_or_class_definition_node.lineno,
             'definition_start_line_offset':module_function_or_class_definition_node.col_offset,
             'definition_end_line_index':module_function_or_class_definition_node.lineno,
             'definition_end_line_offset':module_function_or_class_definition_node.end_col_offset
             }
        )

        # ordered_function_calls
        ordered_function_call_handles: List[Tuple[str,int]] = []

        logger.debug(f'Function definition node: {module_function_or_class_definition_node.__dict__}')

        for child_node in ast.walk(module_function_or_class_definition_node):
            if isinstance(child_node, ast.Call):
                child_call_node = child_node

                grandchild_node = child_call_node.func

                if isinstance(grandchild_node, ast.Name):
                    called_function_handle = grandchild_node.id
                elif isinstance(grandchild_node, ast.Attribute):
                    called_function_handle = grandchild_node.attr
                else:
                    logger.warning(f'Unexpected Call node func attribute type encountered: {grandchild_node.__dict__} | {type(grandchild_node).__name__}')
                    continue

                logger.debug(f'Child node: {child_call_node.__dict__} | {type(child_call_node).__name__}')
                logger.debug(f'Grandchild node: {grandchild_node.__dict__} | {type(grandchild_node).__name__}')

                ordered_function_call_handles.append((called_function_handle, child_call_node.lineno))

        ordered_function_call_handles.sort(key = lambda x: x[1])
        ordered_function_call_handles = [ordered_function_call_handle[0] for ordered_function_call_handle in ordered_function_call_handles]

        definition_payload.update(ordered_function_calls=ordered_function_call_handles)

        # create function or class definition model and add to storage
        # set the class type
        if isinstance(module_function_or_class_definition_node,ast.FunctionDef):
            recorded_definition = RecordedFunction(**definition_payload)
        elif isinstance(module_function_or_class_definition_node,ast.ClassDef):
            recorded_definition = RecordedClass(**definition_payload)

        recorded_definitions.append(recorded_definition)

    return recorded_definitions


def get_module_level_function_and_class_definition_nodes(module_ast: ast.AST) -> List[Union[ast.FunctionDef,ast.ClassDef]]:
    '''
    Retrieves all the module level function and class definition nodes from the specified module's AST.
    Args:
        module_ast:

    Returns:

    '''

    module_level_function_and_class_definition_nodes = []

    for node in ast.walk(module_ast):
        if isinstance(node,ast.FunctionDef) or isinstance(node,ast.ClassDef):
            if node.col_offset == 0:
                module_level_function_and_class_definition_nodes.append(node)

    return module_level_function_and_class_definition_nodes


def get_function_handle_to_id_mapping(recorded_functions: List[RecordedFunction]) -> Dict:
    '''
    Constructs a dict mapping function_handle -> function reference id. Assumes all function handles are unique.

    Args:
        recorded_functions:

    Returns:

    '''

    return dict([(rec_func.function_handle, rec_func.unique_reference_id) for rec_func in recorded_functions])


def map_function_handle_to_id(function_handle: str,
                              function_handle_to_id_mapping: Dict) -> str:

    try:
        function_id = function_handle_to_id_mapping[function_handle]
    except KeyError as e:
        function_id = None

    return function_id


def map_function_called_function_handles_to_ids(recorded_functions: List[RecordedFunction]) -> List[RecordedFunction]:
    '''
    Utility function that creates a mapping from function handle -> function id based on the inputs recorded_functions.
    Assumes function handles are unique.
    Then maps all the function handles in the recorded_functions' ordered_function_calls argument to function ids, and
    returns the updated list of RecordedFunctions objects.

    Args:
        recorded_functions:

    Returns:

    '''

    function_handle_to_id_mapping = get_function_handle_to_id_mapping(recorded_functions)

    cleaned_functions = []

    for recorded_function in recorded_functions:
        cleaned_function = recorded_function.copy()

        ordered_function_call_ids = [
            map_function_handle_to_id(function_handle=function_call,
                                      function_handle_to_id_mapping=function_handle_to_id_mapping) \
            for function_call in recorded_function.ordered_function_calls
        ]

        ordered_function_call_ids = [called_function_id for called_function_id in ordered_function_call_ids if called_function_id is not None]

        cleaned_function.ordered_function_calls = ordered_function_call_ids

        cleaned_functions.append(cleaned_function)

    return cleaned_functions


def record_all_functions_from_modules(recorded_modules: List[RecordedModule]) -> List[RecordedFunction]:

    all_functions = []

    for module in recorded_modules:
        # capture all function definitions in this module and convert into RecordedFunction type objects
        all_functions.extend(record_functions_from_module(module))

    # resolve function calls: map called handles onto the function id where a match can be found, otherwise remove the
    # called handle from the attribute ordered_function_calls
    all_functions_cleaned = map_function_called_function_handles_to_ids(recorded_functions=all_functions)

    logger.info(f'Recorded remaining function meta data.')
    logger.debug(f'Recorded functions meta data (including scope and calls): {all_functions_cleaned}')

    return all_functions_cleaned