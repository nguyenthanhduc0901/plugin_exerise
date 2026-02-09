# provider/ingestion_plugin.py
from typing import Any, Dict
import psycopg2

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class IngestionPluginProvider(ToolProvider):

    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """
        Validate credential dict contains required DB fields and can connect.
        Expected keys: db_host, db_port, db_name, db_user, db_password
        """
        try:
            required = ["db_host", "db_port", "db_name", "db_user", "db_password"]
            for k in required:
                if k not in credentials or credentials[k] in (None, ""):
                    raise ValueError(f"Missing credential: {k}")

            # Try a short DB connection to validate credentials
            conn = psycopg2.connect(
                host=credentials["db_host"],
                port=int(credentials["db_port"]),
                dbname=credentials["db_name"],
                user=credentials["db_user"],
                password=credentials["db_password"],
                connect_timeout=5
            )
            conn.close()

        except Exception as e:
            # Wrap in ToolProviderCredentialValidationError so Dify shows proper error
            raise ToolProviderCredentialValidationError(str(e))
