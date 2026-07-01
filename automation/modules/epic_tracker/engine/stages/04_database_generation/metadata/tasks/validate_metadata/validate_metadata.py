"""Validates the generic database metadata model and metadata task wiring."""

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

    stage_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if parent.name == "04_database_generation"
            and (parent / "metadata").is_dir()
            and (parent / "implementations").is_dir()
        ),
        None,
    )
    if stage_root is not None:
        stage_support = stage_root / "support"
        if str(stage_support) not in sys.path:
            sys.path.insert(0, str(stage_support))
        if str(stage_root) not in sys.path:
            sys.path.append(str(stage_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file
from db_path_utils import get_db_root, resolve_application_stage_config_path


class ValidateMetadataScript(BaseScript):
    """Validates database-neutral metadata before generators consume it."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.db_root = get_db_root(__file__)
        self.metadata_root = self._resolve_db_path("metadataRoot")
        self.tasks_root = self.script_directory.parent
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.table_schemas: dict[str, dict[str, Any]] = {}
        self.table_modules: dict[str, str] = {}

    def run(self) -> None:
        started = time.perf_counter()

        database_metadata = self._validate_database_metadata()
        self._validate_task_model()
        self._validate_modules()
        self._validate_foreign_keys()
        self._validate_generate_task_contract()
        self._validate_remove_task_contract()

        status = "PASSED" if not self.errors else "FAILED"
        report = {
            "scriptName": self.script_name,
            "summary": {
                "status": status,
                "metadataRoot": self.to_project_relative_path(self.metadata_root),
                "taskRoot": self.to_project_relative_path(self.tasks_root),
                "tableCount": len(self.table_schemas),
                "errorCount": len(self.errors),
                "warningCount": len(self.warnings),
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            },
            "database": database_metadata,
            "validatedTables": sorted(self.table_schemas.keys()),
            "errors": self.errors,
            "warnings": self.warnings,
        }
        self.write_json_report(report)

        if self.errors:
            print_failed(f"validate_metadata: {len(self.errors)} error(s)")
            raise SystemExit(1)

        warning_suffix = f", {len(self.warnings)} warning(s)" if self.warnings else ""
        print_passed(f"validate_metadata: validated {len(self.table_schemas)} table(s){warning_suffix}")

    def _resolve_db_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return resolve_application_stage_config_path(self.db_root, self.config, config_key)

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
            implementation_path = self.metadata_root.parent / "implementations" / implementation_name / "database.json"
            implementation_metadata = self._read_required_json(implementation_path)
            if isinstance(implementation_metadata, dict):
                implementation_type = implementation_metadata.get("databaseType")
                if implementation_type != implementation_name:
                    self.errors.append(
                        "Implementation config databaseType must match currentImplementation "
                        f"('{implementation_name}')."
                    )
        return database_metadata

    def _validate_task_model(self) -> None:
        if not self.config.get("validateTaskModel", True):
            return

        expected_task_folders = self.config.get("expectedTaskFolders", [])
        if not isinstance(expected_task_folders, list):
            self.errors.append("Config value 'expectedTaskFolders' must be a list.")
            expected_task_folders = []

        for task_folder in expected_task_folders:
            task_name = str(task_folder)
            task_root = self.tasks_root / task_name
            if not task_root.is_dir():
                self.errors.append(f"Expected metadata task folder does not exist: {task_name}")
                continue
            task_script = task_root / f"{task_name}.py"
            task_config = task_root / "config" / f"{task_name}.json"
            if not task_script.is_file():
                self.errors.append(f"Expected metadata task script does not exist: {self.to_project_relative_path(task_script)}")
            if not task_config.is_file():
                self.errors.append(f"Expected metadata task config does not exist: {self.to_project_relative_path(task_config)}")

        forbidden_task_folders = self.config.get("forbiddenTaskFolders", [])
        if not isinstance(forbidden_task_folders, list):
            self.errors.append("Config value 'forbiddenTaskFolders' must be a list.")
            return
        for task_folder in forbidden_task_folders:
            task_root = self.tasks_root / str(task_folder)
            if task_root.exists():
                self.errors.append(f"Forbidden legacy metadata task folder exists: {self.to_project_relative_path(task_root)}")

    def _validate_modules(self) -> None:
        module_roots = self.config.get("moduleRoots", [])
        if not isinstance(module_roots, list):
            self.errors.append("Config value 'moduleRoots' must be a list.")
            return

        for module_root_value in module_roots:
            module_name = str(module_root_value)
            module_root = self.metadata_root / "modules" / module_name
            self._validate_module(module_root, module_name)

    def _validate_module(self, module_root: Path, module_name: str) -> None:
        if not module_root.exists():
            self.errors.append(f"Module folder does not exist: {self.to_project_relative_path(module_root)}")
            return

        tables_root = module_root / "tables"
        tables_json_path = module_root / "tables.json"
        tables_json = self._read_required_json(tables_json_path)
        tables = tables_json.get("tables", []) if isinstance(tables_json, dict) else []
        if not isinstance(tables, list):
            self.errors.append(f"tables.json must contain a list field named 'tables': {self.to_project_relative_path(tables_json_path)}")
            return
        if not tables_root.is_dir():
            if tables:
                self.errors.append(f"Module tables folder does not exist: {self.to_project_relative_path(tables_root)}")
            return

        table_names = [str(table_name) for table_name in tables]
        if len(table_names) != len(set(table_names)):
            self.errors.append(f"Duplicate table names found in {self.to_project_relative_path(tables_json_path)}")

        for table_name in table_names:
            if not table_name or table_name.strip() != table_name:
                self.errors.append(f"Invalid table name in {self.to_project_relative_path(tables_json_path)}: '{table_name}'")
            self._validate_table(module_root, module_name, table_name)

        listed_table_names = set(table_names)
        actual_table_folder_names = {path.name for path in tables_root.iterdir() if path.is_dir()}
        unlisted_folders = sorted(actual_table_folder_names - listed_table_names)
        missing_folders = sorted(listed_table_names - actual_table_folder_names)

        for table_name in missing_folders:
            self.errors.append(
                f"Table '{table_name}' is listed in {self.to_project_relative_path(tables_json_path)} "
                "but the table folder does not exist."
            )
        for table_name in unlisted_folders:
            self.errors.append(
                f"Table folder exists but is not listed in {self.to_project_relative_path(tables_json_path)}: "
                f"{table_name}"
            )

    def _validate_table(self, module_root: Path, module_name: str, table_name: str) -> None:
        table_root = module_root / "tables" / table_name
        if not table_root.exists():
            return

        schema = self._read_required_json(table_root / "schema.json")
        data = self._read_required_json(table_root / "data.json")
        if isinstance(schema, dict):
            self._validate_schema(module_name, table_name, schema, table_root)
        if isinstance(data, dict):
            self._validate_data(table_name, schema if isinstance(schema, dict) else {}, data)

    def _validate_schema(self, module_name: str, table_name: str, schema: dict[str, Any], table_root: Path) -> None:
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
        if not primary_key:
            self.warnings.append(f"Table '{table_name}' does not define a primary key.")
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
        self.table_modules[table_name] = module_name

    def _validate_foreign_key_shape(self, table_name: str, column_names: list[str], foreign_key: Any) -> None:
        if not isinstance(foreign_key, dict):
            self.errors.append(f"Table '{table_name}' contains a non-object foreign key definition.")
            return
        columns = foreign_key.get("columns", [])
        references = foreign_key.get("references", {})
        referenced_table = references.get("table") if isinstance(references, dict) else None
        referenced_columns = references.get("columns", []) if isinstance(references, dict) else []

        if "name" in foreign_key and (not isinstance(foreign_key.get("name"), str) or not foreign_key.get("name")):
            self.errors.append(f"Table '{table_name}' foreign key name must be a non-empty string when present.")
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

    def _validate_data(self, table_name: str, schema: dict[str, Any], data: dict[str, Any]) -> None:
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
        primary_key = schema.get("primaryKey", [])
        primary_key_tuples: set[tuple[Any, ...]] = set()

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
            if isinstance(primary_key, list) and primary_key and all(key in row for key in primary_key):
                key_tuple = tuple(row[key] for key in primary_key)
                if key_tuple in primary_key_tuples:
                    self.errors.append(f"Table '{table_name}' row {row_index} duplicates primary key value {key_tuple}.")
                primary_key_tuples.add(key_tuple)

    def _validate_generate_task_contract(self) -> None:
        if not self.config.get("validateGenerateTask", True):
            return

        task_root = self.tasks_root / "generate_table_metadata"
        task_config = self._read_optional_json(task_root / "config" / "generate_table_metadata.json")
        if not isinstance(task_config, dict):
            self.errors.append("generate_table_metadata config must contain a JSON object.")
            return

        if task_config.get("scriptName") != "generate_table_metadata":
            self.errors.append("generate_table_metadata config scriptName must be 'generate_table_metadata'.")

        specifications = task_config.get("architectureSpecifications")
        if not isinstance(specifications, list) or not specifications:
            self.errors.append("generate_table_metadata config must contain a non-empty architectureSpecifications list.")
            return

        seen_names: set[str] = set()
        for index, specification in enumerate(specifications):
            if not isinstance(specification, dict):
                self.errors.append(f"architectureSpecifications[{index}] must be an object.")
                continue
            name = specification.get("name")
            path_value = specification.get("path")
            generated_path_value = specification.get("generatedTablesPath")
            if not isinstance(name, str) or not name:
                self.errors.append(f"architectureSpecifications[{index}] must define a non-empty name.")
            elif name in seen_names:
                self.errors.append(f"Duplicate architecture specification name: {name}")
            else:
                seen_names.add(name)
            self._validate_db_relative_json_file(path_value, f"architectureSpecifications[{index}].path")
            self._validate_stage_relative_json_file(
                generated_path_value,
                f"architectureSpecifications[{index}].generatedTablesPath",
            )

            generated_payload = (
                self._read_optional_json(resolve_application_stage_config_path(self.db_root, {**self.config, "__path": generated_path_value}, "__path"))
                if isinstance(generated_path_value, str)
                else None
            )
            if isinstance(generated_payload, dict):
                self._validate_generated_tables_payload(generated_payload, generated_path_value)

    def _validate_generated_tables_payload(self, payload: dict[str, Any], generated_path_value: str) -> None:
        tables = payload.get("tables")
        if not isinstance(tables, list):
            self.errors.append(f"Generated table batch must contain a list field named 'tables': {generated_path_value}")
            return
        generated_table_names: list[str] = []
        for index, table in enumerate(tables):
            if not isinstance(table, dict):
                self.errors.append(f"Generated table batch entry {index} must be an object: {generated_path_value}")
                continue
            table_name = table.get("name")
            if not isinstance(table_name, str) or not table_name:
                self.errors.append(f"Generated table batch entry {index} must define a non-empty name: {generated_path_value}")
                continue
            generated_table_names.append(table_name)
            if "schema" not in table or not isinstance(table.get("schema"), dict):
                self.errors.append(f"Generated table '{table_name}' must contain a schema object.")
            if "data" not in table or not isinstance(table.get("data"), dict):
                self.errors.append(f"Generated table '{table_name}' must contain a data object.")

        if len(generated_table_names) != len(set(generated_table_names)):
            self.errors.append(f"Generated table batch contains duplicate table names: {generated_path_value}")

    def _validate_remove_task_contract(self) -> None:
        if not self.config.get("validateRemoveTask", True):
            return

        task_root = self.tasks_root / "remove_metadata_tables"
        task_config = self._read_optional_json(task_root / "config" / "remove_metadata_tables.json")
        if not isinstance(task_config, dict):
            self.errors.append("remove_metadata_tables config must contain a JSON object.")
            return

        if task_config.get("scriptName") != "remove_metadata_tables":
            self.errors.append("remove_metadata_tables config scriptName must be 'remove_metadata_tables'.")
        if not isinstance(task_config.get("targetMetadataRoot"), str) or not task_config.get("targetMetadataRoot"):
            self.errors.append("remove_metadata_tables config must define targetMetadataRoot.")
        if not isinstance(task_config.get("targetModule"), str) or not task_config.get("targetModule"):
            self.errors.append("remove_metadata_tables config must define targetModule.")

        tables = task_config.get("tables")
        if not isinstance(tables, list):
            self.errors.append("remove_metadata_tables config tables must be a list.")
            return
        for index, table_name in enumerate(tables):
            if not isinstance(table_name, str) or not table_name:
                self.errors.append(f"remove_metadata_tables config tables[{index}] must be a non-empty string.")


    def _validate_db_relative_json_file(self, path_value: Any, field_name: str) -> None:
        self._validate_stage_relative_json_file(path_value, field_name)

    def _validate_stage_relative_json_file(self, path_value: Any, field_name: str) -> None:
        if not isinstance(path_value, str) or not path_value:
            self.errors.append(f"{field_name} must be a non-empty path string.")
            return
        if not path_value.endswith(".json"):
            self.errors.append(f"{field_name} must point to a JSON file: {path_value}")
        resolved_path = resolve_application_stage_config_path(self.db_root, {**self.config, "__path": path_value}, "__path")
        if not resolved_path.is_file():
            self.errors.append(f"{field_name} does not exist: {self.to_project_relative_path(resolved_path)}")

    def _read_required_json(self, file_path: Path) -> Any:
        if not file_path.exists():
            self.errors.append(f"Required JSON file does not exist: {self.to_project_relative_path(file_path)}")
            return {}
        try:
            return read_json_file(file_path)
        except Exception as exc:  # noqa: BLE001 - report validation failure with the path.
            self.errors.append(f"Could not read JSON file {self.to_project_relative_path(file_path)}: {exc}")
            return {}

    def _read_optional_json(self, file_path: Path) -> Any:
        try:
            return read_json_file(file_path)
        except Exception as exc:  # noqa: BLE001 - report validation failure with the path.
            self.errors.append(f"Could not read JSON file {self.to_project_relative_path(file_path)}: {exc}")
            return None


if __name__ == "__main__":
    ValidateMetadataScript().run()
