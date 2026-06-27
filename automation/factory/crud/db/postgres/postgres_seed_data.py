"""
Seeds the PostgreSQL application database with development data.

Run after postgres_create_schema.py:

    python -m scripts.db.postgres.postgres_create_schema
    python -m scripts.db.postgres.postgres_seed_data
"""

import sys
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json


def _configure_project_import_path() -> None:
    project_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "shared").is_dir()
        ),
        None,
    )

    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.config_resolution import ConfigurationResolver
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file
from scripts.shared.script_path_utils import get_path


class PostgreSQLSeedDataScript(BaseScript):
    """Inserts PostgreSQL seed data from structured database and seed configuration."""

    CONNECTION_KEYS = ["host", "port", "databaseName", "username", "password"]

    def __init__(self):
        super().__init__(__file__)
        self.database_config = self._load_database_config()
        self.config_resolver = ConfigurationResolver(default_source_name="database.json")
        self.application_connection_config = self._resolve_application_connection_config()
        self.inserted_rows_by_table = {}
        self.verified_rows_by_table = {}

    def run(self) -> None:
        self._configure_backend_import_path()
        self._validate_database_type()
        self._execute_seed_data()
        self._verify_seed_data()

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
        environment_variables = self.database_config.get("environmentVariables", {})
        return self.config_resolver.resolve_group(
            group_name="application",
            configured_values=self.database_config.get("applicationConnection"),
            environment_variables=environment_variables.get("application", {}),
            keys=self.CONNECTION_KEYS,
            casts={"port": int},
            sensitive_keys={"password"},
        )

    def _execute_seed_data(self) -> None:
        conn = self._get_application_connection()

        try:
            cursor = conn.cursor()

            for seed_group in self._get_seed_groups():
                table_name = self._get_required_string(seed_group, "table", "Every seed group must contain 'table'.")
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

    def _verify_seed_data(self) -> None:
        conn = self._get_application_connection()

        try:
            cursor = conn.cursor()

            for seed_group in self._get_seed_groups():
                table_name = self._get_required_string(seed_group, "table", "Every seed group must contain 'table'.")
                expected_rows = seed_group.get("rows", [])

                if not isinstance(expected_rows, list):
                    raise ValueError("Seed group 'rows' must be a list.")

                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
                )
                actual_count = cursor.fetchone()[0]
                self.verified_rows_by_table[table_name] = actual_count

                if actual_count < len(expected_rows):
                    raise RuntimeError(
                        f"PostgreSQL seed verification failed for table '{table_name}': "
                        f"expected at least {len(expected_rows)} rows, found {actual_count}."
                    )
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
        total_verified_rows = sum(self.verified_rows_by_table.values())

        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "seed_data"),
            "configurationResolution": self.config_resolver.to_report(),
            "summary": {
                "status": "PASSED",
                "databaseName": self.application_connection_config["databaseName"],
                "host": self.application_connection_config["host"],
                "port": self.application_connection_config["port"],
                "username": self.application_connection_config["username"],
                "seededTableCount": len(self.inserted_rows_by_table),
                "insertedRowCount": total_inserted_rows,
                "verifiedTableCount": len(self.verified_rows_by_table),
                "verifiedRowCount": total_verified_rows,
            },
            "insertedRowsByTable": self.inserted_rows_by_table,
            "verifiedRowsByTable": self.verified_rows_by_table,
        }

    def _write_report(self, report: dict) -> None:
        output_file_path = self.output_directory / f"{self.script_name}_report_{self.timestamp}.json"
        write_json_file(output_file_path, report)

    def _print_success(self, report: dict) -> None:
        print_passed(
            "PostgreSQL seed data inserted and verified. "
            f"Rows: {report['summary']['verifiedRowCount']}"
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
