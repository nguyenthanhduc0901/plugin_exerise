# tools/ingestion_plugin.py
import csv
import io
import requests
import psycopg2

from typing import Any, Generator, Dict
from dataclasses import dataclass
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


EXPECTED_COLUMNS = ["name", "salary", "address", "gpa", "school"]


@dataclass
class DbConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str


class IngestionPluginTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # ❗️KHÔNG in nguyên tool_parameters vì có File object
            safe_log = {k: ("***" if "password" in k else ("<file>" if k == "csv_file" else v))
                        for k, v in tool_parameters.items()}
            print("Tool parameters:", safe_log)

            # 1) Get file object
            file_obj = tool_parameters.get("csv_file")
            if not isinstance(file_obj, dict):
                yield self.create_json_message({"status": "error", "message": "csv_file must be a file object"})
                return
            
            # Debug: log all available keys in file object
            print("File object keys:", list(file_obj.keys()))

            # 2) Safe file name
            file_name = file_obj.get("filename") or file_obj.get("name") or "unknown.csv"

            # 3) Read CSV
            csv_text = self._read_csv_content(file_obj)

            # 4) Parse + validate
            rows = self._parse_csv(csv_text)
            rows = self._validate_data(rows)

            # 5) DB config
            try:
                cfg = DbConfig(
                    host=str(tool_parameters.get("db_host")),
                    port=int(tool_parameters.get("db_port")),
                    dbname=str(tool_parameters.get("db_name")),
                    user=str(tool_parameters.get("db_user")),
                    password=str(tool_parameters.get("db_password")),
                )
            except Exception as e:
                yield self.create_json_message({"status": "error", "message": f"Invalid DB params: {e}"})
                return

            # 6) Insert
            inserted = self._insert_rows(cfg, rows)

            # 7) JSON-safe output
            yield self.create_json_message({
                "status": "success",
                "inserted_rows": inserted,
                "file_name": file_name,
                "expected_columns": EXPECTED_COLUMNS
            })

        except Exception as e:
            # ❗️Trả error JSON-safe, KHÔNG throw raw exception
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })

    def _read_csv_content(self, file_obj: Dict[str, Any]) -> str:
        # Try to get local path first
        local_path = file_obj.get("path") or file_obj.get("file_path") or file_obj.get("local_path")
        
        if local_path:
            # Read from local file
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Failed to read local file: {e}")
        
        # Fallback: download from URL if no local path
        file_url = file_obj.get("url") or file_obj.get("remote_url") or file_obj.get("signed_url")
        if file_url:
            resp = requests.get(file_url, timeout=30)
            if resp.status_code != 200:
                raise ValueError(f"Failed to download CSV (HTTP {resp.status_code})")
            return resp.content.decode("utf-8", errors="replace")
        
        raise ValueError("CSV file missing both local path and URL")

    def _parse_csv(self, content: str) -> list[Dict[str, Any]]:
        reader = csv.DictReader(io.StringIO(content))
        missing = [c for c in EXPECTED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV missing columns: {', '.join(missing)}")

        rows: list[Dict[str, Any]] = []
        for row in reader:
            cleaned = {col: (row.get(col) or "").strip() for col in EXPECTED_COLUMNS}
            rows.append(cleaned)
        return rows

    def _validate_data(self, rows: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        if not rows:
            raise ValueError("CSV has no data rows")

        validated = []
        for idx, row in enumerate(rows, start=1):
            if not row["name"]:
                raise ValueError(f"Row {idx}: 'name' is required")

            if row["salary"]:
                try:
                    row["salary"] = float(row["salary"])
                except Exception:
                    raise ValueError(f"Row {idx}: 'salary' must be a number")
            else:
                row["salary"] = None

            if row["gpa"]:
                try:
                    gpa_val = float(row["gpa"])
                    if not (0 <= gpa_val <= 4.0):
                        raise ValueError
                    row["gpa"] = gpa_val
                except Exception:
                    raise ValueError(f"Row {idx}: 'gpa' must be a number between 0 and 4.0")
            else:
                row["gpa"] = None

            validated.append(row)

        return validated

    def _insert_rows(self, cfg: DbConfig, rows: list[Dict[str, Any]]) -> int:
        values = [(r["name"], r["salary"], r["address"], r["gpa"], r["school"]) for r in rows]

        conn = None
        try:
            conn = psycopg2.connect(
                host=cfg.host,
                port=cfg.port,
                dbname=cfg.dbname,
                user=cfg.user,
                password=cfg.password
            )
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS people (
                            name TEXT NOT NULL,
                            salary DOUBLE PRECISION,
                            address TEXT,
                            gpa DOUBLE PRECISION,
                            school TEXT
                        );
                    """)
                    cur.execute("TRUNCATE TABLE people;")
                    if values:
                        cur.executemany(
                            "INSERT INTO people (name, salary, address, gpa, school) VALUES (%s, %s, %s, %s, %s)",
                            values
                        )
            return len(rows)
        except psycopg2.Error as exc:
            if conn:
                conn.rollback()
            raise ValueError(f"Database error: {exc}") from exc
        finally:
            if conn:
                conn.close()


__all__ = ["IngestionPluginTool"]
