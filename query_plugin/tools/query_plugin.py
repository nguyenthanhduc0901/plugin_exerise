from collections.abc import Generator
from typing import Any
import psycopg2

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class QueryPluginTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            name = (tool_parameters.get('name') or tool_parameters.get('query') or '').strip()
            if not name:
                yield self.create_json_message({'status': 'error', 'message': 'Name parameter required'})
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
                SELECT id, name, salary, address, gpa, school, created_at
                FROM csv_data
                WHERE name ILIKE %s
                ORDER BY created_at DESC
                LIMIT 50
            """, (f'%{name}%',))
            
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            if not rows:
                yield self.create_json_message({
                    'status': 'success',
                    'message': f'No records found for "{name}"',
                    'count': 0,
                    'results': []
                })
                return
            
            results = []
            for row in rows:
                results.append({
                    'id': row[0],
                    'name': row[1],
                    'salary': float(row[2]) if row[2] else None,
                    'address': row[3],
                    'gpa': float(row[4]) if row[4] else None,
                    'school': row[5],
                    'created_at': str(row[6])
                })
            
            formatted_text = f"Found {len(results)} record(s) for '{name}':\n\n"
            for idx, result in enumerate(results, 1):
                formatted_text += f"{idx}. {result['name']}\n"
                formatted_text += f"   Salary: ${result['salary']}\n" if result['salary'] else "   Salary: N/A\n"
                formatted_text += f"   Address: {result['address']}\n" if result['address'] else "   Address: N/A\n"
                formatted_text += f"   GPA: {result['gpa']}\n" if result['gpa'] else "   GPA: N/A\n"
                formatted_text += f"   School: {result['school']}\n\n" if result['school'] else "   School: N/A\n\n"
            
            yield self.create_json_message({
                'status': 'success',
                'message': formatted_text,
                'count': len(results),
                'results': results
            })
        
        except Exception as e:
            yield self.create_json_message({'status': 'error', 'message': str(e)})
