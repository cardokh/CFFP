"""Generates or registers PostgreSQL table metadata from new_tables.json table names."""

import re
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path


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


_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class GenerateTableMetadataTask(BaseScript):
    """Task-level entry point for generating staged PostgreSQL table metadata."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_required_object("metadataPaths")
        self.template_paths = self._get_optional_object("templatePaths")
        self.options = self._get_optional_object("options")
        self.validation = self._get_optional_object("validation")
        self.generated_files: list[str] = []
        self.registered_entities: list[str] = []
        self.generated_tables: list[str] = []
        self.validation_result = None

    def run(self) -> None:
        started = time.perf_counter()

        try:
            table_entries = self._read_new_table_entries()

            if not table_entries:
                self.write_json_report(self._build_report("PASSED", started, skipped=True))
                print_passed("generate_table_metadata: no new tables found; skipped")
                return

            seen_table_names: set[str] = set()
            for table_entry in table_entries:
                table_name = self._get_table_name(table_entry)
                if table_name in seen_table_names:
                    raise ValueError(f"Duplicate table '{table_name}' found in new_tables.json.")
                seen_table_names.add(table_name)

                if isinstance(table_entry, dict):
                    self._generate_table_metadata(table_name, table_entry)
                else:
                    self._validate_existing_table_metadata(table_name)

                if self.options.get("registerInAddedEntities", True) is True:
                    self._register_added_entity(table_name)

                self.generated_tables.append(table_name)

            if self.options.get("runValidation", True) is True:
                self.validation_result = self._run_validation()
                if self.validation_result["status"] != "PASSED":
                    self.write_json_report(self._build_report("FAILED", started))
                    raise RuntimeError(
                        "generate_table_metadata validation failed. "
                        "See generate_table_metadata/validator/output for details."
                    )

            self.write_json_report(self._build_report("PASSED", started))
            print_passed(f"generate_table_metadata: metadata generated for {len(self.generated_tables)} table(s)")
        except Exception:
            if not self.get_output_file_path().exists():
                self.write_json_report(self._build_report("FAILED", started))
            raise

    def _get_required_object(self, key: str) -> dict:
        value = self.config.get(key)
        if not isinstance(value, dict):
            raise ValueError(f"Config must contain {key} object.")
        return value

    def _get_optional_object(self, key: str) -> dict:
        value = self.config.get(key, {})
        if not isinstance(value, dict):
            raise ValueError(f"Config {key} must be an object when provided.")
        return value

    def _read_new_table_entries(self) -> list[str | dict]:
        path_value = self._get_required_config_path(self.metadata_paths, "newTablesPath")
        config = read_json_file(self.project_root / path_value)
        if not isinstance(config, dict):
            raise ValueError("new_tables.json must contain a JSON object.")
        tables = config.get("tables", [])
        if not isinstance(tables, list):
            raise ValueError("new_tables.json must contain a tables list.")
        for table in tables:
            if not isinstance(table, (str, dict)):
                raise ValueError("Every new_tables.json table entry must be a table name string or a table definition object.")
        return tables

    def _get_table_name(self, table_entry: str | dict) -> str:
        if isinstance(table_entry, str):
            table_name = table_entry
        else:
            table_name = self._get_required_string(table_entry, "table", "Every table definition must contain non-empty table.")

        if not _NAME_PATTERN.match(table_name):
            raise ValueError(f"Table '{table_name}' must use lowercase snake_case and start with a letter.")
        return table_name

    def _generate_table_metadata(self, table_name: str, definition: dict) -> None:
        self._validate_table_definition(table_name, definition)
        schema_definition = self._build_schema_definition(definition)
        seed_definition = self._build_seed_definition(table_name, definition)
        self._write_schema_file(table_name, schema_definition)
        self._write_seed_file(table_name, seed_definition)

    def _validate_table_definition(self, table_name: str, definition: dict) -> None:
        columns = definition.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Table '{table_name}' must contain non-empty columns list.")

        column_names = []
        for column in columns:
            if not isinstance(column, dict):
                raise ValueError(f"Every column for '{table_name}' must be an object.")
            column_name = self._get_required_string(column, "name", f"Every column for '{table_name}' must contain non-empty name.")
            if not _NAME_PATTERN.match(column_name):
                raise ValueError(f"Column '{column_name}' must use lowercase snake_case and start with a letter.")
            self._get_required_string(column, "type", f"Column '{column_name}' must contain non-empty type.")
            if column_name in column_names:
                raise ValueError(f"Duplicate column '{column_name}' found for table '{table_name}'.")
            column_names.append(column_name)

        constraints = definition.get("constraints", [])
        if not isinstance(constraints, list):
            raise ValueError(f"Table '{table_name}' constraints must be a list when provided.")
        for constraint in constraints:
            self._validate_constraint(table_name, constraint, column_names)

        seed_data = definition.get("seedData", {"rows": []})
        if not isinstance(seed_data, dict):
            raise ValueError(f"Table '{table_name}' seedData must be an object when provided.")
        rows = seed_data.get("rows", [])
        if not isinstance(rows, list):
            raise ValueError(f"Table '{table_name}' seedData.rows must be a list when provided.")
        conflict_column = seed_data.get("conflictColumn", "")
        if rows and (not isinstance(conflict_column, str) or not conflict_column):
            raise ValueError(f"Table '{table_name}' seedData.conflictColumn is required when rows exist.")
        if conflict_column and conflict_column not in column_names:
            raise ValueError(f"Table '{table_name}' seedData.conflictColumn '{conflict_column}' does not match a table column.")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every seedData row for '{table_name}' must be an object.")
            unknown_columns = sorted(set(row.keys()) - set(column_names))
            if unknown_columns:
                raise ValueError(f"Table '{table_name}' seed row contains unknown columns: {', '.join(unknown_columns)}")

    def _validate_existing_table_metadata(self, table_name: str) -> None:
        schema_path = self._get_entity_folder(table_name) / "schema.json"
        seed_path = self._get_entity_folder(table_name) / "seed_data.json"
        if not schema_path.exists():
            raise ValueError(f"Missing staged schema metadata for '{table_name}': {schema_path}")
        if not seed_path.exists():
            raise ValueError(f"Missing staged seed metadata for '{table_name}': {seed_path}")

        schema_definition = read_json_file(schema_path)
        seed_definition = read_json_file(seed_path)
        if not isinstance(schema_definition, dict):
            raise ValueError(f"Staged schema metadata for '{table_name}' must be an object.")
        if not isinstance(seed_definition, dict):
            raise ValueError(f"Staged seed metadata for '{table_name}' must be an object.")
        self._validate_schema_shape(table_name, schema_definition)
        self._validate_seed_shape(table_name, seed_definition, schema_definition)

    def _validate_constraint(self, table_name: str, constraint: dict, column_names: list[str]) -> None:
        if not isinstance(constraint, dict):
            raise ValueError(f"Every constraint for '{table_name}' must be an object.")
        constraint_type = self._get_required_string(constraint, "type", "Every constraint must contain non-empty type.")
        constraint_columns = constraint.get("columns", [])
        if constraint_columns:
            if not isinstance(constraint_columns, list) or not all(isinstance(column, str) and column for column in constraint_columns):
                raise ValueError(f"Constraint '{constraint_type}' columns must be a list of non-empty strings.")
            missing_columns = sorted(set(constraint_columns) - set(column_names))
            if missing_columns:
                raise ValueError(f"Constraint '{constraint_type}' references unknown columns: {', '.join(missing_columns)}")
        if constraint_type == "foreignKey":
            references = constraint.get("references")
            if not isinstance(references, dict):
                raise ValueError("foreignKey constraint must contain references object.")
            reference_table = self._get_required_string(references, "table", "foreignKey references must contain table.")
            if not _NAME_PATTERN.match(reference_table):
                raise ValueError(f"Foreign key reference table '{reference_table}' must use lowercase snake_case.")
            reference_columns = references.get("columns")
            if not isinstance(reference_columns, list) or not reference_columns:
                raise ValueError("foreignKey references.columns must be a non-empty list.")
            if not all(isinstance(column, str) and column for column in reference_columns):
                raise ValueError("foreignKey references.columns must contain non-empty strings.")

    def _validate_schema_shape(self, table_name: str, schema: dict) -> None:
        columns = schema.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema metadata for '{table_name}' must contain non-empty columns list.")
        column_names = []
        for column in columns:
            if not isinstance(column, dict):
                raise ValueError(f"Every column for '{table_name}' must be an object.")
            column_name = self._get_required_string(column, "name", f"Every column for '{table_name}' must contain non-empty name.")
            if not _NAME_PATTERN.match(column_name):
                raise ValueError(f"Column '{column_name}' must use lowercase snake_case and start with a letter.")
            self._get_required_string(column, "type", f"Column '{column_name}' must contain non-empty type.")
            if column_name in column_names:
                raise ValueError(f"Duplicate column '{column_name}' found for table '{table_name}'.")
            column_names.append(column_name)
        constraints = schema.get("constraints", [])
        if not isinstance(constraints, list):
            raise ValueError(f"Schema constraints for '{table_name}' must be a list when provided.")
        for constraint in constraints:
            self._validate_constraint(table_name, constraint, column_names)

    def _validate_seed_shape(self, table_name: str, seed: dict, schema: dict) -> None:
        seed_table_name = self._get_required_string(seed, "table", f"Seed metadata for '{table_name}' must contain table.")
        if seed_table_name != table_name:
            raise ValueError(f"Seed metadata table '{seed_table_name}' does not match '{table_name}'.")
        rows = seed.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"Seed metadata for '{table_name}' must contain rows list.")
        conflict_column = seed.get("conflictColumn", "")
        if rows and (not isinstance(conflict_column, str) or not conflict_column):
            raise ValueError(f"Seed metadata for '{table_name}' must contain conflictColumn when rows are present.")
        column_names = {column["name"] for column in schema["columns"]}
        if conflict_column and conflict_column not in column_names:
            raise ValueError(f"Seed conflictColumn '{conflict_column}' does not match a schema column.")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every seed row for '{table_name}' must be an object.")
            unknown_columns = sorted(set(row.keys()) - column_names)
            if unknown_columns:
                raise ValueError(f"Seed row contains unknown columns: {', '.join(unknown_columns)}")

    def _build_schema_definition(self, definition: dict) -> dict:
        schema = deepcopy(self._read_template("schemaTemplatePath"))
        schema["columns"] = deepcopy(definition["columns"])
        schema["constraints"] = deepcopy(definition.get("constraints", []))
        return schema

    def _build_seed_definition(self, table_name: str, definition: dict) -> dict:
        seed_data = definition.get("seedData", {})
        seed = deepcopy(self._read_template("seedDataTemplatePath"))
        seed["table"] = table_name
        seed["conflictColumn"] = seed_data.get("conflictColumn", "")
        seed["rows"] = deepcopy(seed_data.get("rows", []))
        return seed

    def _read_template(self, key: str) -> dict:
        path_value = self._get_required_config_path(self.template_paths, key)
        template = read_json_file(self.project_root / path_value)
        if not isinstance(template, dict):
            raise ValueError(f"Template '{key}' must contain a JSON object.")
        return template

    def _write_schema_file(self, table_name: str, schema_definition: dict) -> None:
        self._write_metadata_file(self._get_entity_folder(table_name) / "schema.json", schema_definition)

    def _write_seed_file(self, table_name: str, seed_definition: dict) -> None:
        self._write_metadata_file(self._get_entity_folder(table_name) / "seed_data.json", seed_definition)

    def _write_metadata_file(self, path: Path, definition: dict) -> None:
        if path.exists() and self.options.get("replaceExistingEntityFiles", True) is not True:
            raise ValueError(f"Metadata file already exists and replaceExistingEntityFiles is false: {path}")
        write_json_file(path, definition)
        self.generated_files.append(self.to_project_relative_path(path))

    def _get_entity_folder(self, table_name: str) -> Path:
        root = self._get_required_config_path(self.metadata_paths, "addedEntityMetadataRoot")
        return self.project_root / root / table_name

    def _register_added_entity(self, table_name: str) -> None:
        added_entities_path = self.project_root / self._get_required_config_path(self.metadata_paths, "addedEntitiesPath")
        added_entities_config = read_json_file(added_entities_path)
        entities = added_entities_config.get("entities")
        if not isinstance(entities, list):
            raise ValueError("added_entities.json must contain entities list.")
        if not all(isinstance(entity, str) and entity for entity in entities):
            raise ValueError("Every added_entities.json entry must be a non-empty string.")
        if table_name not in entities:
            entities.append(table_name)
            write_json_file(added_entities_path, added_entities_config)
            self.registered_entities.append(table_name)

    def _run_validation(self) -> dict:
        script_path_value = self._get_required_config_path(self.validation, "scriptPath")
        script_path = self.project_root / script_path_value
        if not script_path.exists():
            raise ValueError(f"Validation script not found: {script_path}")

        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "name": "validate_generate_table_metadata",
            "status": "PASSED" if completed.returncode == 0 else "FAILED",
            "scriptPath": self.to_project_relative_path(script_path),
            "durationSeconds": round(time.perf_counter() - started, 4),
            "returnCode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _build_report(self, status: str, started: float, skipped: bool = False) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "generate_postgres_table_metadata"),
            "summary": {
                "status": status,
                "skipped": skipped,
                "generatedTableCount": len(self.generated_tables),
                "generatedFileCount": len(self.generated_files),
                "registeredEntityCount": len(self.registered_entities),
                "durationSeconds": round(time.perf_counter() - started, 4),
            },
            "generatedTables": self.generated_tables,
            "generatedFiles": self.generated_files,
            "registeredEntities": self.registered_entities,
            "validation": self.validation_result,
        }

    def _get_required_string(self, source: dict, key: str, message: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(message)
        return value

    def _get_required_config_path(self, source: dict, key: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Config path '{key}' must be a non-empty string.")
        return value


if __name__ == "__main__":
    GenerateTableMetadataTask().run()
