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
            
            # Get database credentials from db_config object (passed from db_health_check)
            db_config = tool_parameters.get("db_config", {})
            host = db_config.get("host")
            port = int(db_config.get("port", 5432))
            dbname = db_config.get("dbname")
            user = db_config.get("user")
            password = db_config.get("password")
            
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
                
                # Check if row already exists before inserting
                where_conditions = []
                check_values = []
                for i, col in enumerate(df.columns):
                    where_conditions.append(f'"{col}" = %s')
                    check_values.append(values[i])
                
                where_clause = ' AND '.join(where_conditions)
                check_query = f'SELECT 1 FROM employee WHERE {where_clause}'
                
                cursor.execute(check_query, check_values)
                if cursor.fetchone() is None:
                    # Row doesn't exist, so insert it
                    placeholders = ', '.join(['%s'] * len(values))
                    column_names = ', '.join([f'"{col}"' for col in df.columns])
                    insert_query = f'INSERT INTO employee ({column_names}) VALUES ({placeholders})'
                    cursor.execute(insert_query, values)
                    rows_inserted += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            message = f"Successfully imported {rows_inserted} rows to employee table"
            yield self.create_text_message(message)
            
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
