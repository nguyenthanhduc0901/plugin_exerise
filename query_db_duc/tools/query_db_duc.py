from collections.abc import Generator
from typing import Any
import psycopg2
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class QueryDbDucTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # Get SQL query from LLM node (JSON string with "sql" field)
            query_input = tool_parameters.get("query")
            
            # Parse JSON from LLM output
            if isinstance(query_input, str):
                query_data = json.loads(query_input)
            else:
                query_data = query_input
            
            sql_query = query_data.get("sql")
            
            if not sql_query:
                yield self.create_text_message("Error: No SQL query provided")
                return
            
            # Get database credentials from db_config object
            db_config = tool_parameters.get("db_config", {})
            host = db_config.get("host")
            port = int(db_config.get("port", 5432))
            dbname = db_config.get("dbname")
            user = db_config.get("user")
            password = db_config.get("password")
            
            # Connect to database
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(sql_query)
            
            # Fetch results
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Convert results to list of dictionaries
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            
            # Return results as JSON
            yield self.create_json_message({
                "rows": results,
                "row_count": len(results),
                "columns": columns
            })
            
        except json.JSONDecodeError as e:
            yield self.create_text_message(f"Error parsing query JSON: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error executing query: {str(e)}")
