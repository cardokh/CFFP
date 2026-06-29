"""Inserts PostgreSQL seed data from the generic database metadata model."""

import json
import sys
import time
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json


def _configure_project_import_path() -> None:
    project_root = next(
        (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.config_resolution import ConfigurationResolver
from scripts.shared.script_console_utils import print_passed
from scripts.shared.script_json_utils import read_json_file

from automation.factory.crud.db.implementations.postgres.support.dependency_resolver import sort_schemas_by_dependency


class InsertDataScript(BaseScript):
    """Inserts PostgreSQL seed data and writes the executed SQL artifact."""

    CONNECTION_KEYS = ["host", "port", "databaseName", "username", "password"]

    def __init__(self) -> None:
        super().__init__(__file__)
        self.metadata_root = self._resolve_project_path("metadataRoot")
        self.implementation_root = self._resolve_project_path("implementationRoot")
        self.config_resolver = ConfigurationResolver(default_source_name="database.json")
        self.implementation_metadata = read_json_file(self.implementation_root / "database.json")
        self.application_connection_config = self._resolve_application_connection_config()
        self.tables: list[dict[str, Any]] = []
        self.inserted_rows_by_table: dict[str, int] = {}
        self.verified_rows_by_table: dict[str, int] = {}

    def run(self) -> None:
        started = time.perf_counter()
        self._validate_database_type()
        self.tables = self._load_tables()
        sql_text = self._render_data_sql()

        output_file = self.output_directory / self.config.get("outputFileName", "data.sql")
        output_file.write_text(sql_text, encoding="utf-8")

        if self.config.get("executeSql", True) is True:
            self._execute_seed_data()
            self._verify_seed_data()

        row_count = sum(len(table["data"].get("rows", [])) for table in self.tables)
        self.write_json_report({
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "insert_postgres_seed_data_from_generic_metadata"),
            "configurationResolution": self.config_resolver.to_report(),
            "summary": {
                "status": "PASSED",
                "metadataRoot": self.to_project_relative_path(self.metadata_root),
                "implementationRoot": self.to_project_relative_path(self.implementation_root),
                "outputFile": self.to_project_relative_path(output_file),
                "applicationDatabaseName": self.application_connection_config["databaseName"],
                "tableCount": len(self.tables),
                "metadataRowCount": row_count,
                "insertedRowCount": sum(self.inserted_rows_by_table.values()),
                "verifiedRowCount": sum(self.verified_rows_by_table.values()),
                "executed": self.config.get("executeSql", True) is True,
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            },
            "orderedTables": [table["name"] for table in self.tables],
            "insertedRowsByTable": self.inserted_rows_by_table,
            "verifiedRowsByTable": self.verified_rows_by_table,
        })
        action = "inserted" if self.config.get("executeSql", True) is True else "generated"
        print_passed(
            f"insert_data: {action} {row_count} row(s) for {len(self.tables)} table(s); SQL "
            f"{self.to_project_relative_path(output_file)}"
        )

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _validate_database_type(self) -> None:
        if self.implementation_metadata.get("databaseType") != "postgres":
            raise ValueError("insert_data.py requires databaseType 'postgres'.")

    def _resolve_application_connection_config(self) -> dict[str, Any]:
        environment_variables = self.implementation_metadata.get("environmentVariables", {})
        return self.config_resolver.resolve_group(
            group_name="application",
            configured_values=self.implementation_metadata.get("applicationConnection"),
            environment_variables=environment_variables.get("application", {}),
            keys=self.CONNECTION_KEYS,
            casts={"port": int},
            sensitive_keys={"password"},
        )

    def _load_tables(self) -> list[dict[str, Any]]:
        tables_by_name: dict[str, dict[str, Any]] = {}
        schemas: list[dict[str, Any]] = []
        for module_root_value in self.config.get("moduleRoots", []):
            module_root = self.metadata_root / "modules" / str(module_root_value)
            tables_json = read_json_file(module_root / "tables.json")
            for table_name in tables_json.get("tables", []):
                table_root = module_root / "tables" / str(table_name)
                schema = read_json_file(table_root / "schema.json")
                schemas.append(schema)
                tables_by_name[str(table_name)] = {
                    "name": str(table_name),
                    "schema": schema,
                    "data": read_json_file(table_root / "data.json"),
                }

        ordered_schemas = sort_schemas_by_dependency(schemas)
        return [tables_by_name[str(schema["name"])] for schema in ordered_schemas]

    def _execute_seed_data(self) -> None:
        conn = self._get_application_connection()
        try:
            with conn.cursor() as cursor:
                for table in self.tables:
                    inserted_count = self._insert_table_rows(cursor, table)
                    self.inserted_rows_by_table[table["name"]] = inserted_count
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _verify_seed_data(self) -> None:
        conn = self._get_application_connection()
        try:
            with conn.cursor() as cursor:
                for table in self.tables:
                    table_name = table["name"]
                    expected_rows = table["data"].get("rows", [])
                    cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
                    actual_count = cursor.fetchone()[0]
                    self.verified_rows_by_table[table_name] = actual_count
                    if actual_count < len(expected_rows):
                        raise RuntimeError(
                            f"Seed verification failed for table '{table_name}': expected at least "
                            f"{len(expected_rows)} rows, found {actual_count}."
                        )
        finally:
            conn.close()

    def _insert_table_rows(self, cursor: Any, table: dict[str, Any]) -> int:
        table_name = table["name"]
        rows = table["data"].get("rows", [])
        if not rows:
            return 0

        primary_key = table["schema"].get("primaryKey", [])
        inserted_count = 0
        for row in rows:
            columns = list(row.keys())
            values = [self._resolve_row_value(row[column]) for column in columns]
            statement = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(sql.Identifier(column) for column in columns),
                sql.SQL(", ").join(sql.Placeholder() for _ in columns),
            )
            if self.config.get("usePrimaryKeyConflictHandling", True) and primary_key:
                statement += sql.SQL(" ON CONFLICT ({}) DO NOTHING").format(
                    sql.SQL(", ").join(sql.Identifier(column) for column in primary_key)
                )
            cursor.execute(statement, values)
            inserted_count += cursor.rowcount
        return inserted_count

    def _resolve_row_value(self, value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return Json(value)
        return value

    def _render_data_sql(self) -> str:
        lines: list[str] = [
            "-- Generated from automation/factory/crud/db/metadata.",
            "-- Parallel PostgreSQL implementation artifact.",
            "",
        ]
        for table in self.tables:
            table_lines = self._render_table_data(table)
            if table_lines:
                lines.extend(table_lines)
                lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _render_table_data(self, table: dict[str, Any]) -> list[str]:
        table_name = table["name"]
        rows = table["data"].get("rows", [])
        if not rows:
            return [f"-- No seed rows for {table_name}."]

        lines = [f"-- Seed data for {table_name}."]
        primary_key = table["schema"].get("primaryKey", [])
        for row in rows:
            columns = list(row.keys())
            column_sql = ", ".join(self._identifier(column) for column in columns)
            value_sql = ", ".join(self._literal(row[column]) for column in columns)
            statement = f"INSERT INTO {self._identifier(table_name)} ({column_sql}) VALUES ({value_sql})"
            if self.config.get("usePrimaryKeyConflictHandling", True) and primary_key:
                conflict_columns = ", ".join(self._identifier(column) for column in primary_key)
                statement += f" ON CONFLICT ({conflict_columns}) DO NOTHING"
            lines.append(statement + ";")
        return lines

    def _literal(self, value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (dict, list)):
            return "'" + json.dumps(value).replace("'", "''") + "'::jsonb"
        return "'" + str(value).replace("'", "''") + "'"

    def _get_application_connection(self) -> Any:
        return psycopg2.connect(
            host=self.application_connection_config["host"],
            port=self.application_connection_config["port"],
            dbname=self.application_connection_config["databaseName"],
            user=self.application_connection_config["username"],
            password=self.application_connection_config["password"],
        )

    def _identifier(self, value: str) -> str:
        return '"' + str(value).replace('"', '""') + '"'


if __name__ == "__main__":
    InsertDataScript().run()
