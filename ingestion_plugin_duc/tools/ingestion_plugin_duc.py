from collections.abc import Generator
from typing import Any
import psycopg2
import pandas as pd
from io import BytesIO

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

class IngestionPluginDucTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            csv_file = tool_parameters.get("csv_file")
            
            credentials = self.runtime.credentials
            host = credentials.get("host")
            port = credentials.get("port")
            dbname = credentials.get("dbname")
            user = credentials.get("user")
            password = credentials.get("password")
            
            csv_content = csv_file.blob
            df = pd.read_csv(BytesIO(csv_content))
            
            # Connect to database
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            cursor = conn.cursor()
            
            # Create table if not exists
            columns = []
            for col in df.columns:
                columns.append(f'"{col}" TEXT')
            
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS employee (
                {', '.join(columns)}
            )
            """
            cursor.execute(create_table_query)
            
            # Insert data
            rows_inserted = 0
            for _, row in df.iterrows():
                values = [str(v) if pd.notna(v) else None for v in row]
                placeholders = ', '.join(['%s'] * len(values))
                column_names = ', '.join([f'"{col}"' for col in df.columns])
                insert_query = f'INSERT INTO employee ({column_names}) VALUES ({placeholders})'
                cursor.execute(insert_query, values)
                rows_inserted += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            yield self.create_json_message({
                "status": "success",
                "message": f"Successfully imported {rows_inserted} rows to employee table",
                "rows_inserted": rows_inserted,
                "table_name": "employee"
            })
            
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
