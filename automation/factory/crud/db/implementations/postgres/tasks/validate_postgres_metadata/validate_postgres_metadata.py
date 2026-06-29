"""Validates PostgreSQL implementation metadata against the generic metadata model."""

import sys
import time
from pathlib import Path
from typing import Any


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
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file


class ValidatePostgresMetadataScript(BaseScript):
    """Checks that generic metadata can be translated by the PostgreSQL implementation."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.metadata_root = self._resolve_project_path("metadataRoot")
        self.implementation_root = self._resolve_project_path("implementationRoot")
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.table_count = 0

    def run(self) -> None:
        started = time.perf_counter()
        database_metadata = self._read_required_json(self.metadata_root / "database.json")
        implementation_metadata = self._read_required_json(self.implementation_root / "database.json")

        self._validate_database_pointer(database_metadata)
        self._validate_implementation_config(implementation_metadata)
        self._validate_table_metadata()

        status = "PASSED" if not self.errors else "FAILED"
        self.write_json_report({
            "scriptName": self.script_name,
            "summary": {
                "status": status,
                "metadataRoot": self.to_project_relative_path(self.metadata_root),
                "implementationRoot": self.to_project_relative_path(self.implementation_root),
                "tableCount": self.table_count,
                "errorCount": len(self.errors),
                "warningCount": len(self.warnings),
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            },
            "errors": self.errors,
            "warnings": self.warnings,
        })

        if self.errors:
            print_failed(f"validate_postgres_metadata: {len(self.errors)} error(s)")
            raise SystemExit(1)
        print_passed(f"validate_postgres_metadata: validated {self.table_count} table(s)")

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _validate_database_pointer(self, database_metadata: Any) -> None:
        if not isinstance(database_metadata, dict):
            self.errors.append("metadata/database.json must contain a JSON object.")
            return
        current_implementation = database_metadata.get("currentImplementation")
        if current_implementation != "postgres":
            self.errors.append("metadata/database.json currentImplementation must be 'postgres' for this task.")

    def _validate_implementation_config(self, implementation_metadata: Any) -> None:
        if not isinstance(implementation_metadata, dict):
            self.errors.append("implementations/postgres/database.json must contain a JSON object.")
            return
        if implementation_metadata.get("databaseType") != "postgres":
            self.errors.append("implementations/postgres/database.json databaseType must be 'postgres'.")

        required_groups = self.config.get("requiredConnectionGroups", [])
        required_fields = self.config.get("requiredConnectionFields", [])
        for group_name in required_groups:
            group = implementation_metadata.get(group_name)
            if not isinstance(group, dict):
                self.errors.append(f"Postgres config is missing connection group '{group_name}'.")
                continue
            for field_name in required_fields:
                if field_name not in group or group.get(field_name) in (None, ""):
                    self.errors.append(f"Postgres config '{group_name}' is missing field '{field_name}'.")

    def _validate_table_metadata(self) -> None:
        supported_types = set(self.config.get("supportedGenericTypes", {}).keys())
        supported_defaults = set(self.config.get("supportedDefaultTypes", {}).keys())
        for module_root_value in self.config.get("moduleRoots", []):
            module_root = self.metadata_root / "modules" / str(module_root_value)
            tables_json = self._read_required_json(module_root / "tables.json")
            tables = tables_json.get("tables", []) if isinstance(tables_json, dict) else []
            if not isinstance(tables, list):
                self.errors.append(f"tables.json must contain a list field named 'tables': {module_root}")
                continue
            for table_name in tables:
                self.table_count += 1
                schema = self._read_required_json(module_root / "tables" / str(table_name) / "schema.json")
                if isinstance(schema, dict):
                    self._validate_schema(str(table_name), schema, supported_types, supported_defaults)

    def _validate_schema(
        self,
        table_name: str,
        schema: dict[str, Any],
        supported_types: set[str],
        supported_defaults: set[str],
    ) -> None:
        for column in schema.get("columns", []):
            if not isinstance(column, dict):
                continue
            column_name = column.get("name", "<unknown>")
            generic_type = column.get("type")
            if generic_type not in supported_types:
                self.errors.append(
                    f"Table '{table_name}' column '{column_name}' uses unsupported Postgres generic type '{generic_type}'."
                )
            default = column.get("default")
            if isinstance(default, dict):
                default_type = default.get("type")
                if default_type is None and generic_type == "json":
                    continue
                if default_type not in supported_defaults:
                    self.errors.append(
                        f"Table '{table_name}' column '{column_name}' uses unsupported Postgres default type '{default_type}'."
                    )

    def _read_required_json(self, file_path: Path) -> Any:
        if not file_path.exists():
            self.errors.append(f"Required JSON file does not exist: {self.to_project_relative_path(file_path)}")
            return {}
        try:
            return read_json_file(file_path)
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f"Could not read JSON file {self.to_project_relative_path(file_path)}: {exc}")
            return {}


if __name__ == "__main__":
    ValidatePostgresMetadataScript().run()
