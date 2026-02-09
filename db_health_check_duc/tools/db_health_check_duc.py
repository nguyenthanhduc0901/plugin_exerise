from collections.abc import Generator
from typing import Any
import psycopg2

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class DbHealthCheckDucTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        result = "false"
        message = "Database connection failed"
        host = tool_parameters.get("host")
        port = tool_parameters.get("port")
        dbname = tool_parameters.get("dbname")
        user = tool_parameters.get("user")
        password = tool_parameters.get("password")
        
        try:
            port = int(port) if port else 5432
            
            # Test connection
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            conn.close()
            result = "true"
            message = f"Database connection successful. Connected to {dbname} on {host}:{port}"
        except Exception as e:
            message = f"Database connection failed: {str(e)}"
        
        # Return text message for display
        yield self.create_text_message(message)
        # Return health status and credentials as object for next step
        yield self.create_variable_message("healthy", result)
        yield self.create_variable_message("db_config", {
            "host": host,
            "port": port,
            "dbname": dbname,
            "user": user,
            "password": password
        })
