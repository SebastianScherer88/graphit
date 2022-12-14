from pydantic import BaseModel
from pathlib import Path
from typing import List

class RecordedModule(BaseModel):
    unique_reference_id: str
    file_path: Path
    import_path: str
    reference_directory: str = ''


class RecordedFunction(BaseModel):
    unique_reference_id: str
    function_handle: str
    source_module_reference_id: str
    definition_start_line_index: int
    definition_start_line_offset: int
    definition_end_line_index: int
    definition_end_line_offset: int
    ordered_function_calls: List[str]

    def test_1(self):
        pass

    def test_2(self):
        pass

class RecordedClass(RecordedFunction):
    pass