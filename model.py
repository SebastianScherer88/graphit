from pydantic import BaseModel
from pathlib import Path
from typing import List

class RecordedModule(BaseModel):
    file_path: Path
    import_path: str
    reference_directory: str = ''


class RecordedFunctionBasic(BaseModel):
    unique_function_reference_id: str
    function_handle: str
    source_module: RecordedModule


class RecordedFunction(RecordedFunctionBasic):
    definition_start_line_index: int
    definition_end_line_index: int
    ordered_function_calls: List[RecordedFunctionBasic]
