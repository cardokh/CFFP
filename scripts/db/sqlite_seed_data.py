"""
Seeds the SQLite database with development data for the LLA application.

Run this script after sqlite_create_schema.py:

    python scripts/db/sqlite_create_schema.py
    python scripts/db/sqlite_seed_data.py
"""

import sys
from pathlib import Path
from typing import Any

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_json_utils import (
    read_json_file,
    write_json_file,
)
from scripts.shared.script_path_utils import (
    get_path,
)


class SQLiteSeedDataScript(BaseScript):
    """
    Inserts SQLite seed data from structured database and seed configuration.
    """

    def __init__(self):
        super().__init__(__file__)
        self.database_config = self._load_database_config()
        self.database_path = self._resolve_database_path()
        self.inserted_rows_by_table = {}

    def run(self) -> None:
        self._configure_backend_import_path()
        self._execute_seed_data()

        report = self._build_report()
        self._write_report(report)
        self._print_success(report)

    def _load_database_config(self) -> dict:
        database_config_path = self._resolve_config_path("databaseConfigPath")

        return read_json_file(database_config_path)

    def _resolve_config_path(
        self,
        config_key: str,
    ) -> Path:
        config_path = self.config.get(config_key)

        if not isinstance(config_path, str) or not config_path:
            raise ValueError(f"Config must contain '{config_key}'.")

        return self.project_root / config_path

    def _configure_backend_import_path(self) -> None:
        backend_path_key = self.database_config.get("backendPathKey")

        if not isinstance(backend_path_key, str) or not backend_path_key:
            raise ValueError("database.json must contain 'backendPathKey'.")

        backend_path = get_path(backend_path_key)

        if str(backend_path) not in sys.path:
            sys.path.append(str(backend_path))

    def _resolve_database_path(self) -> Path:
        database_path_key = self.database_config.get("databasePathKey")

        if not isinstance(database_path_key, str) or not database_path_key:
            raise ValueError("database.json must contain 'databasePathKey'.")

        return get_path(database_path_key)

    def _execute_seed_data(self) -> None:
        if self.database_config.get("databaseType") != "sqlite":
            raise ValueError("sqlite_seed_data.py requires databaseType 'sqlite'.")

        from src.ccore.infrastructure.database import DatabaseManager

        db = DatabaseManager(str(self.database_path))
        conn = db.get_connection()

        try:
            if self.database_config.get("enableForeignKeys") is True:
                conn.execute("PRAGMA foreign_keys = ON")

            cursor = conn.cursor()

            for seed_group in self._get_seed_groups():
                self._insert_seed_group(
                    cursor,
                    seed_group,
                )

            conn.commit()

        finally:
            conn.close()

    def _get_seed_groups(self) -> list[dict]:
        seed_groups = self.config.get("seedGroups")

        if not isinstance(seed_groups, list) or not seed_groups:
            raise ValueError(
                "sqlite_seed_data.json must contain non-empty 'seedGroups'."
            )

        return seed_groups

    def _insert_seed_group(
        self,
        cursor: Any,
        seed_group: dict,
    ) -> None:
        table_name = self._get_required_string(
            seed_group,
            "table",
            "Seed group must contain 'table'.",
        )

        rows = seed_group.get("rows")

        if not isinstance(rows, list):
            raise ValueError(f"Seed group '{table_name}' must contain 'rows' list.")

        for row in rows:
            self._insert_row(
                cursor,
                table_name,
                row,
            )

        self.inserted_rows_by_table[table_name] = self.inserted_rows_by_table.get(
            table_name, 0
        ) + len(rows)

    def _insert_row(
        self,
        cursor: Any,
        table_name: str,
        row: dict,
    ) -> None:
        if not isinstance(row, dict) or not row:
            raise ValueError(f"Seed row for table '{table_name}' must be an object.")

        resolved_row = self._resolve_row_values(row)

        columns = list(resolved_row.keys())
        values = [resolved_row[column] for column in columns]

        column_sql = ", ".join(columns)
        placeholder_sql = ", ".join(["?" for _ in columns])

        cursor.execute(
            f"INSERT INTO {table_name} ({column_sql}) VALUES ({placeholder_sql})",
            values,
        )

    def _resolve_row_values(
        self,
        row: dict,
    ) -> dict:
        resolved_row = {}

        for column_name, value in row.items():
            resolved_row[column_name] = self._resolve_value(value)

        return resolved_row

    def _resolve_value(
        self,
        value: Any,
    ) -> Any:
        if not isinstance(value, dict):
            return value

        transform_name = value.get("transform")

        if transform_name == "hashPassword":
            plain_text = value.get("value")

            if not isinstance(plain_text, str):
                raise ValueError("hashPassword transform requires string 'value'.")

            return self._hash_password(plain_text)

        raise ValueError(f"Unsupported seed value transform '{transform_name}'.")

    def _hash_password(
        self,
        plain_text: str,
    ) -> str:
        from src.core.users.password_service import PasswordService

        password_service = PasswordService()

        return password_service.hash_password(plain_text)

    def _get_required_string(
        self,
        source: dict,
        key: str,
        error_message: str,
    ) -> str:
        value = source.get(key)

        if not isinstance(value, str) or not value:
            raise ValueError(error_message)

        return value

    def _build_report(self) -> dict:
        total_inserted_rows = sum(self.inserted_rows_by_table.values())

        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "seed_data",
            ),
            "summary": {
                "status": "PASSED",
                "databasePath": self.to_project_relative_path(self.database_path),
                "seededTableCount": len(self.inserted_rows_by_table),
                "insertedRowCount": total_inserted_rows,
            },
            "insertedRowsByTable": self.inserted_rows_by_table,
        }

    def _write_report(
        self,
        report: dict,
    ) -> None:
        output_file_path = (
            self.output_directory / f"{self.script_name}_report_{self.timestamp}.json"
        )

        write_json_file(
            output_file_path,
            report,
        )

    def _print_success(
        self,
        report: dict,
    ) -> None:
        inserted_row_count = report["summary"]["insertedRowCount"]

        print_passed(
            (
                f"{self.script_name}: SQLite seed data inserted "
                f"with {inserted_row_count} row(s)"
            )
        )


def main() -> None:
    try:
        SQLiteSeedDataScript().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
