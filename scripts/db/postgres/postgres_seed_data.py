"""
Seeds the PostgreSQL application database with development data.

Run after postgres_create_schema.py:

    python -m scripts.db.postgres.postgres_create_schema
    python -m scripts.db.postgres.postgres_seed_data
"""

import os
import sys
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file
from scripts.shared.script_path_utils import get_path


class PostgreSQLSeedDataScript(BaseScript):
    """
    Inserts PostgreSQL seed data from structured database and seed configuration.
    """

    def __init__(self):
        super().__init__(__file__)
        self.database_config = self._load_database_config()
        self.application_connection_config = self._resolve_application_connection_config()
        self.inserted_rows_by_table = {}

    def run(self) -> None:
        self._configure_backend_import_path()
        self._validate_database_type()
        self._execute_seed_data()

        report = self._build_report()
        self._write_report(report)
        self._print_success(report)

    def _load_database_config(self) -> dict:
        return read_json_file(self._resolve_config_path("databaseConfigPath"))

    def _resolve_config_path(self, config_key: str) -> Path:
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

    def _validate_database_type(self) -> None:
        if self.database_config.get("databaseType") != "postgres":
            raise ValueError("postgres_seed_data.py requires databaseType 'postgres'.")

    def _resolve_application_connection_config(self) -> dict:
        configured_connection = self.database_config.get("applicationConnection")
        environment_variables = self.database_config.get("environmentVariables", {})
        application_environment_variables = environment_variables.get("application", {})

        if not isinstance(configured_connection, dict):
            raise ValueError("database.json must contain 'applicationConnection' object.")

        if not isinstance(application_environment_variables, dict):
            raise ValueError("database.json environmentVariables must contain 'application' object.")

        return {
            "host": self._resolve_connection_value("host", configured_connection, application_environment_variables),
            "port": int(self._resolve_connection_value("port", configured_connection, application_environment_variables)),
            "databaseName": self._resolve_connection_value("databaseName", configured_connection, application_environment_variables),
            "username": self._resolve_connection_value("username", configured_connection, application_environment_variables),
            "password": self._resolve_connection_value("password", configured_connection, application_environment_variables),
        }

    def _resolve_connection_value(
        self,
        key: str,
        configured_connection: dict,
        environment_variables: dict,
    ) -> Any:
        environment_variable_name = environment_variables.get(key)

        if isinstance(environment_variable_name, str) and environment_variable_name:
            environment_value = os.environ.get(environment_variable_name)

            if environment_value not in (None, ""):
                return environment_value

        configured_value = configured_connection.get(key)

        if configured_value in (None, ""):
            raise ValueError(f"PostgreSQL connection value '{key}' is not configured.")

        return configured_value

    def _execute_seed_data(self) -> None:
        conn = self._get_application_connection()

        try:
            cursor = conn.cursor()

            for seed_group in self._get_seed_groups():
                table_name = self._get_required_string(
                    seed_group,
                    "table",
                    "Every seed group must contain 'table'.",
                )
                conflict_column = self._get_required_string(
                    seed_group,
                    "conflictColumn",
                    "Every PostgreSQL seed group must contain 'conflictColumn'.",
                )
                rows = seed_group.get("rows", [])

                if not isinstance(rows, list):
                    raise ValueError("Seed group 'rows' must be a list.")

                inserted_count = 0

                for row in rows:
                    if not isinstance(row, dict):
                        raise ValueError("Every seed row must be an object.")

                    inserted_count += self._insert_row(
                        cursor,
                        table_name,
                        conflict_column,
                        self._resolve_row_values(row),
                    )

                self.inserted_rows_by_table[table_name] = inserted_count

            conn.commit()
        finally:
            conn.close()

    def _get_seed_groups(self) -> list[dict]:
        seed_groups = self.config.get("seedGroups")

        if not isinstance(seed_groups, list):
            raise ValueError("postgres_seed_data.json must contain 'seedGroups' list.")

        return seed_groups

    def _insert_row(self, cursor: Any, table_name: str, conflict_column: str, row: dict) -> int:
        if not row:
            return 0

        columns = list(row.keys())
        values = [row[column] for column in columns]
        placeholders = [sql.Placeholder() for _ in columns]

        cursor.execute(
            sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO NOTHING").format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(sql.Identifier(column) for column in columns),
                sql.SQL(", ").join(placeholders),
                sql.Identifier(conflict_column),
            ),
            values,
        )

        return cursor.rowcount

    def _resolve_row_values(self, row: dict) -> dict:
        resolved_row = {}

        for column_name, value in row.items():
            resolved_row[column_name] = self._resolve_value(value)

        return resolved_row

    def _resolve_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return Json(value)

        return value

    def _get_application_connection(self) -> Any:
        return psycopg2.connect(
            host=self.application_connection_config["host"],
            port=self.application_connection_config["port"],
            dbname=self.application_connection_config["databaseName"],
            user=self.application_connection_config["username"],
            password=self.application_connection_config["password"],
        )

    def _get_required_string(self, source: dict, key: str, error_message: str) -> str:
        value = source.get(key)

        if not isinstance(value, str) or not value:
            raise ValueError(error_message)

        return value

    def _build_report(self) -> dict:
        total_inserted_rows = sum(self.inserted_rows_by_table.values())

        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "seed_data"),
            "summary": {
                "status": "PASSED",
                "databaseName": self.application_connection_config["databaseName"],
                "host": self.application_connection_config["host"],
                "port": self.application_connection_config["port"],
                "username": self.application_connection_config["username"],
                "seededTableCount": len(self.inserted_rows_by_table),
                "insertedRowCount": total_inserted_rows,
            },
            "insertedRowsByTable": self.inserted_rows_by_table,
        }

    def _write_report(self, report: dict) -> None:
        output_file_path = self.output_directory / f"{self.script_name}_report_{self.timestamp}.json"
        write_json_file(output_file_path, report)

    def _print_success(self, report: dict) -> None:
        print_passed(
            f"PostgreSQL seed data inserted. Rows: {report['summary']['insertedRowCount']}"
        )


def main() -> None:
    script = PostgreSQLSeedDataScript()

    try:
        script.run()
    except Exception as exc:
        print_failed(f"PostgreSQL seed data failed: {exc}")
        raise


if __name__ == "__main__":
    main()
