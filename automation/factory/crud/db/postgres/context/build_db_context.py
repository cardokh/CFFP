"""Builds DB-only handoff context files for downstream automation tasks."""

import sys
from pathlib import Path
from typing import Any


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
from scripts.shared.script_console_utils import print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file


class PostgreSQLBuildDbContextScript(BaseScript):
    """Creates database-focused context files for backend/frontend generators to consume."""

    def __init__(self):
        super().__init__(__file__)
        self.database_config = read_json_file(self._resolve_project_path("databaseConfigPath"))
        self.entities_config = read_json_file(self._resolve_project_path("entitiesConfigPath"))
        self.entity_metadata_root = self._resolve_project_path("entityMetadataRoot")
        self.context_output_root = self._resolve_project_path("contextOutputRoot")
        self.master_context_path = self.context_output_root / "master_context.json"
        self.table_context_root = self.context_output_root / "tables"
        self.written_table_context_paths: list[Path] = []

    def run(self) -> None:
        self._validate_database_type()
        selected_entities = self._get_entity_names()
        table_contexts = []

        self.table_context_root.mkdir(parents=True, exist_ok=True)
        for entity_name in selected_entities:
            table_context = self._build_table_context(entity_name)
            table_context_path = self.table_context_root / f"{entity_name}.json"
            write_json_file(table_context_path, table_context)
            self.written_table_context_paths.append(table_context_path)
            table_contexts.append(
                {
                    "tableName": entity_name,
                    "contextFile": self.to_project_relative_path(table_context_path),
                    "seedRowCount": table_context["seedRowCount"],
                }
            )

        master_context = self._build_master_context(selected_entities, table_contexts)
        write_json_file(self.master_context_path, master_context)

        report = self._build_report(selected_entities)
        self.write_json_report(report)
        print_passed(
            f"build_db_context: wrote master context and {len(self.written_table_context_paths)} table context files"
        )

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _validate_database_type(self) -> None:
        if self.database_config.get("databaseType") != "postgres":
            raise ValueError("build_db_context.py requires databaseType 'postgres'.")

    def _get_entity_names(self) -> list[str]:
        entities = self.entities_config.get("entities")
        if not isinstance(entities, list) or not entities:
            raise ValueError("entities.json must contain non-empty 'entities'.")
        for entity_name in entities:
            if not isinstance(entity_name, str) or not entity_name:
                raise ValueError("Every entities.json entry must be a non-empty string.")
        if len(entities) != len(set(entities)):
            raise ValueError("entities.json must not contain duplicate entity names.")
        return entities

    def _build_master_context(self, selected_entities: list[str], table_contexts: list[dict]) -> dict:
        application_connection = self.database_config.get("applicationConnection", {})
        if not isinstance(application_connection, dict):
            raise ValueError("database.json applicationConnection must be an object.")
        database_name = application_connection.get("databaseName")
        if not isinstance(database_name, str) or not database_name:
            raise ValueError("database.json applicationConnection.databaseName must be a non-empty string.")

        return {
            "contextType": "database_handoff_context",
            "scope": "database_only",
            "database": {
                "engine": self.database_config.get("databaseType"),
                "name": database_name,
                "schema": self.config.get("databaseSchema", "public"),
            },
            "selectedTables": selected_entities,
            "tableCount": len(selected_entities),
            "tableContexts": table_contexts,
            "rules": {
                "containsBackendNaming": False,
                "containsFrontendNaming": False,
                "downstreamGeneratorsMustApplyTheirOwnBlueprints": True,
            },
        }

    def _build_table_context(self, entity_name: str) -> dict:
        schema_path = self.entity_metadata_root / entity_name / "schema.json"
        seed_path = self.entity_metadata_root / entity_name / "seed_data.json"
        if not schema_path.exists():
            raise ValueError(f"Missing schema metadata for entity '{entity_name}': {schema_path}")
        if not seed_path.exists():
            raise ValueError(f"Missing seed metadata for entity '{entity_name}': {seed_path}")

        schema = read_json_file(schema_path)
        seed = read_json_file(seed_path)
        columns = self._get_columns(entity_name, schema)
        constraints = self._get_constraints(entity_name, schema)
        foreign_keys = [constraint for constraint in constraints if constraint.get("type") == "foreignKey"]
        primary_key = self._get_primary_key(columns, constraints)
        seed_rows = seed.get("rows", [])
        if not isinstance(seed_rows, list):
            raise ValueError(f"Seed metadata for '{entity_name}' must contain rows list.")

        return {
            "contextType": "database_table_context",
            "scope": "database_only",
            "tableName": entity_name,
            "sourceFiles": {
                "schema": self.to_project_relative_path(schema_path),
                "seedData": self.to_project_relative_path(seed_path),
            },
            "columns": [self._build_column_context(column) for column in columns],
            "primaryKey": primary_key,
            "foreignKeys": foreign_keys,
            "constraints": constraints,
            "indexes": schema.get("indexes", []),
            "seedRowCount": len(seed_rows),
        }

    def _get_columns(self, entity_name: str, schema: dict) -> list[dict]:
        columns = schema.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema for '{entity_name}' must contain non-empty columns list.")
        return columns

    def _get_constraints(self, entity_name: str, schema: dict) -> list[dict]:
        constraints = schema.get("constraints", [])
        if not isinstance(constraints, list):
            raise ValueError(f"Schema constraints for '{entity_name}' must be a list when provided.")
        return constraints

    def _build_column_context(self, column: dict) -> dict:
        if not isinstance(column, dict):
            raise ValueError("Every column must be an object.")
        column_name = self._get_required_string(column, "name", "Column definition must contain 'name'.")
        data_type = self._get_required_string(column, "type", f"Column '{column_name}' must contain 'type'.")
        return {
            "name": column_name,
            "postgresType": data_type,
            "nullable": column.get("nullable", True),
            "default": column.get("default"),
            "primaryKey": column.get("primaryKey", False),
            "unique": column.get("unique", False),
        }

    def _get_primary_key(self, columns: list[dict], constraints: list[dict]) -> list[str]:
        constrained_primary_keys = [
            constraint.get("columns", [])
            for constraint in constraints
            if constraint.get("type") == "primaryKey"
        ]
        if constrained_primary_keys:
            return constrained_primary_keys[0]
        return [column["name"] for column in columns if column.get("primaryKey") is True]

    def _get_required_string(self, source: dict, key: str, error_message: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(error_message)
        return value

    def _build_report(self, selected_entities: list[str]) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "build_db_context"),
            "summary": {
                "status": "PASSED",
                "selectedEntityCount": len(selected_entities),
                "tableContextFileCount": len(self.written_table_context_paths),
                "masterContextFile": self.to_project_relative_path(self.master_context_path),
            },
            "output": {
                "masterContextFile": self.to_project_relative_path(self.master_context_path),
                "tableContextFiles": [
                    self.to_project_relative_path(path) for path in self.written_table_context_paths
                ],
            },
        }


if __name__ == "__main__":
    PostgreSQLBuildDbContextScript().run()
