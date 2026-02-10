from collections.abc import Generator
from typing import Any
from io import BytesIO

import openpyxl
import xlrd

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

class Uc03EmptyFileCheckTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file_inputs = tool_parameters.get("file_inputs")

        # Start node may pass a list; some contexts may pass a single File
        file_obj: Any | None = None
        if isinstance(file_inputs, list):
            if len(file_inputs) > 0:
                file_obj = file_inputs[0]
        else:
            file_obj = file_inputs

        if not isinstance(file_obj, File):
            # If we can't read the blob, treat as not-empty to be safe
            yield self.create_variable_message("check_empty", "false")
            return

        filename = (file_obj.filename or "").lower()
        blob = file_obj.blob

        try:
            has_data = False

            if filename.endswith(".xlsx"):
                workbook = openpyxl.load_workbook(
                    filename=BytesIO(blob),
                    read_only=True,
                    data_only=True,
                )
                for worksheet in workbook.worksheets:
                    for row in worksheet.iter_rows(values_only=True):
                        for cell_value in row:
                            if cell_value is None:
                                continue
                            if isinstance(cell_value, str) and cell_value.strip() == "":
                                continue
                            has_data = True
                            break
                        if has_data:
                            break
                    if has_data:
                        break

            elif filename.endswith(".xls"):
                book = xlrd.open_workbook(file_contents=blob)
                for sheet_index in range(book.nsheets):
                    sheet = book.sheet_by_index(sheet_index)
                    for row_index in range(sheet.nrows):
                        for col_index in range(sheet.ncols):
                            cell_value = sheet.cell_value(row_index, col_index)
                            if cell_value is None:
                                continue
                            if isinstance(cell_value, str) and cell_value.strip() == "":
                                continue
                            has_data = True
                            break
                        if has_data:
                            break
                    if has_data:
                        break
            else:
                # Unknown extension => treat as not-empty
                yield self.create_variable_message("check_empty", "false")
                return

            yield self.create_variable_message("check_empty", "true" if not has_data else "false")
        except Exception:
            # If error reading Excel, treat as not-empty
            yield self.create_variable_message("check_empty", "false")
