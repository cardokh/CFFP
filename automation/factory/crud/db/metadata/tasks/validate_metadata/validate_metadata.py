"""Validates the generic database metadata model."""

import sys
import time
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
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file


class ValidateMetadataScript(BaseScript):
    """Validates database-neutral metadata before generators consume it."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.metadata_root = self._resolve_project_path("metadataRoot")
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.table_schemas: dict[str, dict[str, Any]] = {}

    def run(self) -> None:
        started = time.perf_counter()

        database_metadata = self._validate_database_metadata()
        self._validate_modules()
        self._validate_foreign_keys()

        status = "PASSED" if not self.errors else "FAILED"
        report = {
            "scriptName": self.script_name,
            "summary": {
                "status": status,
                "metadataRoot": self.to_project_relative_path(self.metadata_root),
                "tableCount": len(self.table_schemas),
                "errorCount": len(self.errors),
                "warningCount": len(self.warnings),
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            },
            "database": database_metadata,
            "errors": self.errors,
            "warnings": self.warnings,
        }
        self.write_json_report(report)

        if self.errors:
            print_failed(f"validate_metadata: {len(self.errors)} error(s)")
            raise SystemExit(1)

        print_passed(f"validate_metadata: validated {len(self.table_schemas)} table(s)")

    def _resolve_project_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return self.project_root / configured_path

    def _validate_database_metadata(self) -> dict[str, Any]:
        database_path = self.metadata_root / "database.json"
        database_metadata = self._read_required_json(database_path)
        if not isinstance(database_metadata, dict):
            self.errors.append("database.json must contain a JSON object.")
            return {}

        for field_name in self.config.get("requiredDatabaseFields", []):
            if field_name not in database_metadata:
                self.errors.append(f"database.json is missing required field '{field_name}'.")

        implementation_name = database_metadata.get("currentImplementation")
        if not isinstance(implementation_name, str) or not implementation_name:
            self.errors.append("database.json field 'currentImplementation' must be a non-empty string.")
            return database_metadata

        if self.config.get("validateImplementationConfig", True):
            implementation_path = self.metadata_root / "implementations" / implementation_name / "database.json"
            implementation_metadata = self._read_required_json(implementation_path)
            if isinstance(implementation_metadata, dict):
                implementation_type = implementation_metadata.get("databaseType")
                if implementation_type != implementation_name:
                    self.errors.append(
                        "Implementation config databaseType must match currentImplementation "
                        f"('{implementation_name}')."
                    )
        return database_metadata

    def _validate_modules(self) -> None:
        module_roots = self.config.get("moduleRoots", [])
        if not isinstance(module_roots, list):
            self.errors.append("Config value 'moduleRoots' must be a list.")
            return

        for module_root_value in module_roots:
            module_root = self.metadata_root / "modules" / str(module_root_value)
            self._validate_module(module_root)

    def _validate_module(self, module_root: Path) -> None:
        if not module_root.exists():
            self.errors.append(f"Module folder does not exist: {self.to_project_relative_path(module_root)}")
            return

        tables_json = self._read_required_json(module_root / "tables.json")
        tables = tables_json.get("tables", []) if isinstance(tables_json, dict) else []
        if not isinstance(tables, list):
            self.errors.append(f"tables.json must contain a list field named 'tables': {module_root}")
            return

        table_names = [str(table_name) for table_name in tables]
        if len(table_names) != len(set(table_names)):
            self.errors.append(f"Duplicate table names found in {self.to_project_relative_path(module_root / 'tables.json')}")

        for table_name in table_names:
            self._validate_table(module_root, table_name)

    def _validate_table(self, module_root: Path, table_name: str) -> None:
        table_root = module_root / "tables" / table_name
        if not table_root.exists():
            self.errors.append(f"Table folder does not exist: {self.to_project_relative_path(table_root)}")
            return

        schema = self._read_required_json(table_root / "schema.json")
        data = self._read_required_json(table_root / "data.json")
        if isinstance(schema, dict):
            self._validate_schema(table_name, schema, table_root)
        if isinstance(data, dict):
            self._validate_data(table_name, schema if isinstance(schema, dict) else {}, data, table_root)

    def _validate_schema(self, table_name: str, schema: dict[str, Any], table_root: Path) -> None:
        schema_name = schema.get("name")
        if schema_name != table_name:
            self.errors.append(f"schema.json name must match table folder name '{table_name}'.")

        columns = schema.get("columns")
        if not isinstance(columns, list) or not columns:
            self.errors.append(f"Table '{table_name}' must define at least one column.")
            return

        column_names: list[str] = []
        for column in columns:
            if not isinstance(column, dict):
                self.errors.append(f"Table '{table_name}' contains a non-object column definition.")
                continue
            column_name = column.get("name")
            if not isinstance(column_name, str) or not column_name:
                self.errors.append(f"Table '{table_name}' contains a column without a valid name.")
                continue
            column_names.append(column_name)
            if not isinstance(column.get("type"), str) or not column.get("type"):
                self.errors.append(f"Table '{table_name}' column '{column_name}' is missing a valid generic type.")
            if "nullable" not in column:
                self.errors.append(f"Table '{table_name}' column '{column_name}' is missing nullable flag.")

        if len(column_names) != len(set(column_names)):
            self.errors.append(f"Table '{table_name}' contains duplicate column names.")

        primary_key = schema.get("primaryKey", [])
        if not isinstance(primary_key, list):
            self.errors.append(f"Table '{table_name}' primaryKey must be a list.")
            primary_key = []
        for primary_key_column in primary_key:
            if primary_key_column not in column_names:
                self.errors.append(f"Table '{table_name}' primary key column '{primary_key_column}' does not exist.")

        foreign_keys = schema.get("foreignKeys", [])
        if not isinstance(foreign_keys, list):
            self.errors.append(f"Table '{table_name}' foreignKeys must be a list.")
            foreign_keys = []
        for foreign_key in foreign_keys:
            self._validate_foreign_key_shape(table_name, column_names, foreign_key)

        self.table_schemas[table_name] = schema

    def _validate_foreign_key_shape(self, table_name: str, column_names: list[str], foreign_key: Any) -> None:
        if not isinstance(foreign_key, dict):
            self.errors.append(f"Table '{table_name}' contains a non-object foreign key definition.")
            return
        columns = foreign_key.get("columns", [])
        references = foreign_key.get("references", {})
        referenced_table = references.get("table") if isinstance(references, dict) else None
        referenced_columns = references.get("columns", []) if isinstance(references, dict) else []

        if not isinstance(columns, list) or not columns:
            self.errors.append(f"Table '{table_name}' foreign key must define one or more columns.")
        for column_name in columns:
            if column_name not in column_names:
                self.errors.append(f"Table '{table_name}' foreign key column '{column_name}' does not exist.")
        if not isinstance(referenced_table, str) or not referenced_table:
            self.errors.append(f"Table '{table_name}' foreign key must define references.table.")
        if not isinstance(referenced_columns, list) or not referenced_columns:
            self.errors.append(f"Table '{table_name}' foreign key must define references.columns.")

    def _validate_foreign_keys(self) -> None:
        for table_name, schema in self.table_schemas.items():
            for foreign_key in schema.get("foreignKeys", []):
                references = foreign_key.get("references", {})
                referenced_table = references.get("table")
                referenced_columns = references.get("columns", [])
                if referenced_table not in self.table_schemas:
                    self.errors.append(f"Table '{table_name}' references unknown table '{referenced_table}'.")
                    continue
                referenced_column_names = {
                    column.get("name")
                    for column in self.table_schemas[referenced_table].get("columns", [])
                    if isinstance(column, dict)
                }
                for referenced_column in referenced_columns:
                    if referenced_column not in referenced_column_names:
                        self.errors.append(
                            f"Table '{table_name}' references unknown column "
                            f"'{referenced_table}.{referenced_column}'."
                        )

    def _validate_data(self, table_name: str, schema: dict[str, Any], data: dict[str, Any], table_root: Path) -> None:
        data_table = data.get("table")
        if data_table != table_name:
            self.errors.append(f"data.json table must match table folder name '{table_name}'.")

        rows = data.get("rows", [])
        if not isinstance(rows, list):
            self.errors.append(f"Table '{table_name}' data rows must be a list.")
            return

        if not self.config.get("validateDataRows", True) or not isinstance(schema, dict):
            return

        columns = schema.get("columns", [])
        column_map = {column.get("name"): column for column in columns if isinstance(column, dict)}
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                self.errors.append(f"Table '{table_name}' row {row_index} must be an object.")
                continue
            for row_column in row.keys():
                if row_column not in column_map:
                    self.errors.append(f"Table '{table_name}' row {row_index} contains unknown column '{row_column}'.")
            for column_name, column in column_map.items():
                if column.get("nullable") is False and column_name not in row and "default" not in column:
                    self.errors.append(
                        f"Table '{table_name}' row {row_index} is missing required column '{column_name}'."
                    )

    def _read_required_json(self, file_path: Path) -> Any:
        if not file_path.exists():
            self.errors.append(f"Required JSON file does not exist: {self.to_project_relative_path(file_path)}")
            return {}
        try:
            return read_json_file(file_path)
        except Exception as exc:  # noqa: BLE001 - report validation failure with the path.
            self.errors.append(f"Could not read JSON file {self.to_project_relative_path(file_path)}: {exc}")
            return {}


if __name__ == "__main__":
    ValidateMetadataScript().run()
