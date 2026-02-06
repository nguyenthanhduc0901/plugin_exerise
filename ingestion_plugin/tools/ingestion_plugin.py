from collections.abc import Generator
from typing import Any
import csv
import io
import psycopg2
from psycopg2.extras import execute_values

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class IngestionPluginTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            csv_file = tool_parameters.get('csv_file') or tool_parameters.get('file')
            if not csv_file:
                yield self.create_json_message({'status': 'error', 'message': 'CSV file required'})
                return
            
            content = csv_file.read() if hasattr(csv_file, 'read') else csv_file
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            stream = io.StringIO(content)
            csv_reader = csv.DictReader(stream)
            
            required_columns = {'name', 'salary', 'address', 'gpa', 'school'}
            if not csv_reader.fieldnames or not required_columns.issubset(set(csv_reader.fieldnames)):
                yield self.create_json_message({
                    'status': 'error',
                    'message': f'CSV must contain: {required_columns}'
                })
                return
            
            creds = self.tool_runtime.tool_runtime_data.get('credentials', {})
            conn = psycopg2.connect(
                host=creds.get('db_host', 'localhost'),
                port=int(creds.get('db_port', 5432)),
                database=creds.get('db_name', 'dify'),
                user=creds.get('db_user', 'postgres'),
                password=creds.get('db_password', '')
            )
            cur = conn.cursor()
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS csv_data (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    salary DECIMAL(15, 2),
                    address TEXT,
                    gpa DECIMAL(3, 2),
                    school VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            rows = []
            row_count = 0
            for row in csv_reader:
                rows.append((
                    row.get('name', '').strip() or None,
                    float(row['salary']) if row.get('salary') else None,
                    row.get('address', '').strip() or None,
                    float(row['gpa']) if row.get('gpa') else None,
                    row.get('school', '').strip() or None
                ))
                row_count += 1
            
            if row_count == 0:
                yield self.create_json_message({'status': 'error', 'message': 'CSV is empty'})
                cur.close()
                conn.close()
                return
            
            execute_values(cur, 'INSERT INTO csv_data (name, salary, address, gpa, school) VALUES %s', rows)
            conn.commit()
            cur.close()
            conn.close()
            
            yield self.create_json_message({
                'status': 'success',
                'message': f'Ingested {row_count} rows',
                'rows_inserted': row_count
            })
        
        except Exception as e:
            yield self.create_json_message({'status': 'error', 'message': str(e)})
