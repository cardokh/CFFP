"""Generates PostgreSQL table metadata from a single new_table.json definition."""

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


_TABLE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class CreatePostgresTableMetadataTask(BaseScript):
    """Task-level entry point for creating staged PostgreSQL table metadata."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_required_object("metadataPaths")
        self.template_paths = self._get_required_object("templatePaths")
        self.options = self._get_optional_object("options")
        self.validation = self._get_optional_object("validation")
        self.generated_files = []
        self.registered_entities = []
        self.validation_result = None

    def run(self) -> None:
        started = time.perf_counter()
        table_name = None

        try:
            new_table = self._read_new_table_definition()

            if not self._has_new_table_definition(new_table):
                self.write_json_report(self._build_report("PASSED", started, None, skipped=True))
                print_passed("create_table_task: no new table definition found; skipped")
                return

            table_name = self._validate_new_table_definition(new_table)
            schema_definition = self._build_schema_definition(new_table)
            seed_definition = self._build_seed_definition(table_name, new_table)

            self._write_schema_file(table_name, schema_definition)
            self._write_seed_file(table_name, seed_definition)

            if self.options.get("registerInAddedEntities", True) is True:
                self._register_added_entity(table_name)

            if self.options.get("runValidation", True) is True:
                self.validation_result = self._run_validation()
                if self.validation_result["status"] != "PASSED":
                    self.write_json_report(self._build_report("FAILED", started, table_name))
                    raise RuntimeError("create_table_task validation failed. See create_table/validator/output for details.")

            self.write_json_report(self._build_report("PASSED", started, table_name))
            print_passed(f"create_table_task: metadata generated for '{table_name}'")
        except Exception:
            if not self.get_output_file_path().exists():
                self.write_json_report(self._build_report("FAILED", started, table_name))
            raise

    def _has_new_table_definition(self, definition: dict) -> bool:
        return bool(definition.get("table") or definition.get("columns") or definition.get("constraints") or definition.get("seedData"))

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

    def _read_new_table_definition(self) -> dict:
        path_value = self._get_required_config_path(self.metadata_paths, "newTablePath")
        definition = read_json_file(self.project_root / path_value)
        if not isinstance(definition, dict):
            raise ValueError("new_table.json must contain one table definition object.")
        return definition

    def _validate_new_table_definition(self, definition: dict) -> str:
        table_name = self._get_required_string(definition, "table", "new_table.json must contain non-empty table.")
        if not _TABLE_NAME_PATTERN.match(table_name):
            raise ValueError("Table name must use lowercase snake_case and start with a letter.")

        columns = definition.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError("new_table.json must contain non-empty columns list.")

        column_names = []
        for column in columns:
            if not isinstance(column, dict):
                raise ValueError("Every column definition must be an object.")
            column_name = self._get_required_string(column, "name", "Every column must contain non-empty name.")
            if not _TABLE_NAME_PATTERN.match(column_name):
                raise ValueError(f"Column '{column_name}' must use lowercase snake_case and start with a letter.")
            self._get_required_string(column, "type", f"Column '{column_name}' must contain non-empty type.")
            if column_name in column_names:
                raise ValueError(f"Duplicate column '{column_name}' found in new_table.json.")
            column_names.append(column_name)

        constraints = definition.get("constraints", [])
        if not isinstance(constraints, list):
            raise ValueError("constraints must be a list when provided.")
        for constraint in constraints:
            self._validate_constraint(constraint, column_names)

        seed_data = definition.get("seedData", {"rows": []})
        if not isinstance(seed_data, dict):
            raise ValueError("seedData must be an object when provided.")
        rows = seed_data.get("rows", [])
        if not isinstance(rows, list):
            raise ValueError("seedData.rows must be a list when provided.")
        conflict_column = seed_data.get("conflictColumn", "")
        if rows and (not isinstance(conflict_column, str) or not conflict_column):
            raise ValueError("seedData.conflictColumn is required when seedData.rows contains entries.")
        if conflict_column and conflict_column not in column_names:
            raise ValueError(f"seedData.conflictColumn '{conflict_column}' does not match a table column.")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("Every seedData row must be an object.")
            unknown_columns = sorted(set(row.keys()) - set(column_names))
            if unknown_columns:
                raise ValueError(f"Seed row contains unknown columns: {', '.join(unknown_columns)}")

        return table_name

    def _validate_constraint(self, constraint: dict, column_names: list[str]) -> None:
        if not isinstance(constraint, dict):
            raise ValueError("Every constraint must be an object.")
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
            if not _TABLE_NAME_PATTERN.match(reference_table):
                raise ValueError(f"Foreign key reference table '{reference_table}' must use lowercase snake_case.")
            reference_columns = references.get("columns")
            if not isinstance(reference_columns, list) or not reference_columns:
                raise ValueError("foreignKey references.columns must be a non-empty list.")
            if not all(isinstance(column, str) and column for column in reference_columns):
                raise ValueError("foreignKey references.columns must contain non-empty strings.")

    def _build_schema_definition(self, definition: dict) -> dict:
        template = self._read_template("schemaTemplatePath")
        schema = deepcopy(template)
        schema["columns"] = deepcopy(definition["columns"])
        schema["constraints"] = deepcopy(definition.get("constraints", []))
        return schema

    def _build_seed_definition(self, table_name: str, definition: dict) -> dict:
        template = self._read_template("seedDataTemplatePath")
        seed_data = definition.get("seedData", {})
        seed = deepcopy(template)
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
        schema_path = self._get_entity_folder(table_name) / "schema.json"
        self._write_metadata_file(schema_path, schema_definition)

    def _write_seed_file(self, table_name: str, seed_definition: dict) -> None:
        seed_path = self._get_entity_folder(table_name) / "seed_data.json"
        self._write_metadata_file(seed_path, seed_definition)

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
            "name": "validate_create_table_metadata",
            "status": "PASSED" if completed.returncode == 0 else "FAILED",
            "scriptPath": self.to_project_relative_path(script_path),
            "durationSeconds": round(time.perf_counter() - started, 4),
            "returnCode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _build_report(self, status: str, started: float, table_name: str | None, skipped: bool = False) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "generate_postgres_table_metadata"),
            "summary": {
                "status": status,
                "skipped": skipped,
                "table": table_name,
                "generatedFileCount": len(self.generated_files),
                "registeredEntityCount": len(self.registered_entities),
                "durationSeconds": round(time.perf_counter() - started, 4),
            },
            "generatedFiles": self.generated_files,
            "registeredEntities": self.registered_entities,
            "validation": self.validation_result,
        }

    def _get_required_config_path(self, source: dict, key: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Config path '{key}' must be a non-empty string.")
        return value

    def _get_required_string(self, source: dict, key: str, error_message: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(error_message)
        return value


if __name__ == "__main__":
    CreatePostgresTableMetadataTask().run()
