"""Seeds PostgreSQL from per-entity metadata files selected by postgres/metadata/entities.json."""

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
from scripts.shared.script_console_utils import print_passed
from scripts.shared.script_json_utils import read_json_file
from scripts.shared.script_path_utils import get_path


class PostgreSQLSeedDbDataScript(BaseScript):
    """Inserts seed data for only the entities listed in postgres/metadata/entities.json."""

    CONNECTION_KEYS = ["host", "port", "databaseName", "username", "password"]

    def __init__(self):
        super().__init__(__file__)
        self.database_config = self._load_database_config()
        self.entities_config = self._load_entities_config()
        self.entity_metadata_root = self._resolve_project_path("entityMetadataRoot")
        self.config_resolver = ConfigurationResolver(default_source_name="database.json")
        self.application_connection_config = self._resolve_application_connection_config()
        self.inserted_rows_by_table = {}
        self.verified_rows_by_table = {}
        self.skipped_seed_groups = []

    def run(self) -> None:
        self._configure_backend_import_path()
        self._validate_database_type()
        self._execute_seed_data()
        self._verify_seed_data()
        report = self._build_report()
        self.write_json_report(report)
        print_passed(
            f"PostgreSQL seed data inserted and verified. Rows: {sum(self.verified_rows_by_table.values())}"
        )

    def _load_database_config(self) -> dict:
        return read_json_file(self._resolve_project_path("databaseConfigPath"))

    def _load_entities_config(self) -> dict:
        return read_json_file(self._resolve_project_path("entitiesConfigPath"))

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _configure_backend_import_path(self) -> None:
        backend_path_key = self.database_config.get("backendPathKey")
        if not isinstance(backend_path_key, str) or not backend_path_key:
            raise ValueError("database.json must contain 'backendPathKey'.")
        backend_path = get_path(backend_path_key)
        if str(backend_path) not in sys.path:
            sys.path.append(str(backend_path))

    def _validate_database_type(self) -> None:
        if self.database_config.get("databaseType") != "postgres":
            raise ValueError("seed_db_data.py requires databaseType 'postgres'.")

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
                rows = seed_group.get("rows", [])
                if not isinstance(rows, list):
                    raise ValueError(f"Seed group rows must be a list: {table_name}")
                if not rows:
                    self.inserted_rows_by_table[table_name] = 0
                    self.skipped_seed_groups.append(table_name)
                    continue
                conflict_column = self._get_required_string(
                    seed_group,
                    "conflictColumn",
                    f"Seed group '{table_name}' must contain 'conflictColumn' when rows are present.",
                )
                inserted_count = 0
                for row in rows:
                    if not isinstance(row, dict):
                        raise ValueError(f"Every seed row for '{table_name}' must be an object.")
                    inserted_count += self._insert_row(cursor, table_name, conflict_column, self._resolve_row_values(row))
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
                    raise ValueError(f"Seed group rows must be a list: {table_name}")
                cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
                actual_count = cursor.fetchone()[0]
                self.verified_rows_by_table[table_name] = actual_count
                if actual_count < len(expected_rows):
                    raise RuntimeError(
                        f"Seed verification failed for table '{table_name}': expected at least {len(expected_rows)} rows, found {actual_count}."
                    )
        finally:
            conn.close()

    def _get_entity_names(self) -> list[str]:
        entities = self.entities_config.get("entities")
        if not isinstance(entities, list):
            raise ValueError("entities.json must contain 'entities' list.")
        for entity in entities:
            if not isinstance(entity, str) or not entity:
                raise ValueError("Every entity entry must be a non-empty string.")
        return entities

    def _get_seed_groups(self) -> list[dict]:
        seed_groups = []
        for entity_name in self._get_entity_names():
            seed_path = self.entity_metadata_root / entity_name / "seed_data.json"
            if not seed_path.exists():
                seed_groups.append({"table": entity_name, "conflictColumn": "", "rows": []})
                continue
            seed_group = read_json_file(seed_path)
            if not isinstance(seed_group, dict):
                raise ValueError(f"Seed metadata for '{entity_name}' must be an object.")
            if seed_group.get("table") != entity_name:
                raise ValueError(f"Seed metadata table does not match entity folder: {entity_name}")
            seed_groups.append(seed_group)
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
        return {column_name: self._resolve_value(value) for column_name, value in row.items()}

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
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "seed_data"),
            "configurationResolution": self.config_resolver.to_report(),
            "summary": {
                "status": "PASSED",
                "applicationDatabaseName": self.application_connection_config["databaseName"],
                "selectedEntityCount": len(self._get_entity_names()),
                "insertedRowCount": sum(self.inserted_rows_by_table.values()),
                "verifiedRowCount": sum(self.verified_rows_by_table.values()),
                "skippedEmptySeedGroupCount": len(self.skipped_seed_groups),
            },
            "entities": self._get_entity_names(),
            "insertedRowsByTable": self.inserted_rows_by_table,
            "verifiedRowsByTable": self.verified_rows_by_table,
            "skippedSeedGroups": self.skipped_seed_groups,
        }


if __name__ == "__main__":
    PostgreSQLSeedDbDataScript().run()
