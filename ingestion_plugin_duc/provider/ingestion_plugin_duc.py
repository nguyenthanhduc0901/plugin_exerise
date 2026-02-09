from typing import Any
import psycopg2

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class IngestionPluginDucProvider(ToolProvider):
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Validate database connection
            host = credentials.get("host")
            port = credentials.get("port")
            dbname = credentials.get("dbname")
            user = credentials.get("user")
            password = credentials.get("password")
            
            # Test connection
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            conn.close()
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))