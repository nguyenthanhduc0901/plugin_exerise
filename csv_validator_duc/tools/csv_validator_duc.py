from collections.abc import Generator
from typing import Any
import pandas as pd
import json
from io import BytesIO

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

class CsvValidatorDucTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        valid = "false"
        message = "CSV validation failed"
        
        try:
            # Get CSV file from parameters
            csv_file: File = tool_parameters.get("csv_file")
            
            if not csv_file:
                message = "CSV file not provided"
            elif csv_file:
                # Read CSV file
                csv_content = csv_file.blob
                df = pd.read_csv(BytesIO(csv_content))
                
                # Validation checks
                if df.empty:
                    message = "CSV file is empty"
                elif len(df.columns) == 0:
                    message = "CSV has no columns"
                elif len(df) == 0:
                    message = "CSV has no data rows"
                else:
                    required_columns = ['name', 'salary', 'address', 'gpa', 'school']
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    
                    if missing_cols:
                        message = f"Missing required columns: {', '.join(missing_cols)}"
                    elif df.isnull().all().any():
                        message = "Some columns contain only null values"
                    else:
                        # Validate salary
                        salary = pd.to_numeric(df['salary'], errors='coerce')
                        if salary.isnull().any():
                            message = "Salary column contains non-numeric values"
                        elif (salary <= 0).any():
                            message = "Salary must be greater than 0"
                        else:
                            # Validate GPA
                            gpa = pd.to_numeric(df['gpa'], errors='coerce')
                            if gpa.isnull().any():
                                message = "GPA column contains non-numeric values"
                            elif ((gpa < 0) | (gpa > 4)).any():
                                message = "GPA must be between 0 and 4"
                            elif df['name'].isnull().any() or df['name'].str.strip().eq('').any():
                                message = "Name column contains empty values"
                            elif df['school'].isnull().any() or df['school'].str.strip().eq('').any():
                                message = "School column contains empty values"
                            elif df['address'].isnull().any() or df['address'].str.strip().eq('').any():
                                message = "Address column contains empty values"
                            else:
                                valid = "true"
                                message = f"CSV is valid. Contains {len(df)} rows and {len(df.columns)} columns"
        except Exception as e:
            message = f"Error reading CSV: {str(e)}"
        
        # Return text message for display
        yield self.create_text_message(message)
        # Return valid variable for workflow logic
        yield self.create_variable_message("valid", valid)
