"""Prepares PostgreSQL entity metadata for added DB entities and validates the result."""

import subprocess
import sys
import time
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


class AddPostgresEntityMetadataTask(BaseScript):
    """Task-level entry point for adding PostgreSQL entity metadata files."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_metadata_paths()
        self.options = self._get_options()
        self.validation = self._get_validation_config()
        self.added_entity_names = self._read_added_entity_names()
        self.updated_entities = []
        self.updated_schema_files = []
        self.updated_seed_files = []
        self.validation_result = None

    def run(self) -> None:
        started = time.perf_counter()
        entities_config = self._read_entities_config()
        self._validate_entities_config(entities_config)

        for entity_name in self.added_entity_names:
            schema_definition = self._read_added_schema_file(entity_name)
            seed_definition = self._read_added_seed_file(entity_name)

            self._validate_schema_definition(entity_name, schema_definition)
            self._validate_seed_definition(entity_name, seed_definition)

            self._upsert_entity_name(entities_config, entity_name)

            self._write_schema_file(entity_name, schema_definition)
            self._write_seed_file(entity_name, seed_definition)

        self._write_entities_config(entities_config)

        if self.options.get("runValidation", True) is True:
            self.validation_result = self._run_validation()
            if self.validation_result["status"] != "PASSED":
                self.write_json_report(self._build_report("FAILED", started))
                raise RuntimeError("add_task validation failed. See postgres/add/validator/output for details.")

        report = self._build_report("PASSED", started)
        self.write_json_report(report)
        print_passed(
            "add_task: "
            f"{len(self.updated_entities)} entities, "
            f"{len(self.updated_schema_files)} schema files, "
            f"{len(self.updated_seed_files)} seed files updated"
        )

    def _get_metadata_paths(self) -> dict:
        metadata_paths = self.config.get("metadataPaths")
        if not isinstance(metadata_paths, dict):
            raise ValueError("Config must contain metadataPaths object.")
        required_keys = [
            "addedEntitiesPath",
            "addedEntityMetadataRoot",
            "entitiesConfigPath",
            "entityMetadataRoot",
        ]
        for key in required_keys:
            if not isinstance(metadata_paths.get(key), str) or not metadata_paths.get(key):
                raise ValueError(f"metadataPaths must contain non-empty '{key}'.")
        return metadata_paths

    def _get_options(self) -> dict:
        options = self.config.get("options", {})
        if not isinstance(options, dict):
            raise ValueError("Config options must be an object when provided.")
        return options

    def _get_validation_config(self) -> dict:
        validation = self.config.get("validation", {})
        if not isinstance(validation, dict):
            raise ValueError("Config validation must be an object when provided.")
        return validation

    def _read_added_entity_names(self) -> list[str]:
        added_entities_config = read_json_file(self.project_root / self.metadata_paths["addedEntitiesPath"])
        entity_names = added_entities_config.get("entities")
        if not isinstance(entity_names, list):
            raise ValueError("added_entities.json must contain entities list.")
        for entity_name in entity_names:
            if not isinstance(entity_name, str) or not entity_name:
                raise ValueError("Every added_entities.json entry must be a non-empty string.")
        if len(entity_names) != len(set(entity_names)):
            raise ValueError("added_entities.json must not contain duplicate entity names.")
        return entity_names

    def _read_added_schema_file(self, entity_name: str) -> dict:
        schema_path = self._get_added_entity_folder(entity_name) / "schema.json"
        if not schema_path.exists():
            raise ValueError(f"Missing added schema metadata: {schema_path}")
        schema_definition = read_json_file(schema_path)
        if not isinstance(schema_definition, dict):
            raise ValueError(f"Added schema for '{entity_name}' must be an object.")
        return schema_definition

    def _read_added_seed_file(self, entity_name: str) -> dict:
        seed_path = self._get_added_entity_folder(entity_name) / "seed_data.json"
        if not seed_path.exists():
            raise ValueError(f"Missing added seed metadata: {seed_path}")
        seed_definition = read_json_file(seed_path)
        if not isinstance(seed_definition, dict):
            raise ValueError(f"Added seed data for '{entity_name}' must be an object.")
        return seed_definition

    def _get_added_entity_folder(self, entity_name: str) -> Path:
        return self.project_root / self.metadata_paths["addedEntityMetadataRoot"] / entity_name

    def _read_entities_config(self) -> dict:
        return read_json_file(self.project_root / self.metadata_paths["entitiesConfigPath"])

    def _write_entities_config(self, entities_config: dict) -> None:
        write_json_file(self.project_root / self.metadata_paths["entitiesConfigPath"], entities_config)

    def _validate_entities_config(self, entities_config: dict) -> None:
        if not isinstance(entities_config.get("entities"), list):
            raise ValueError("entities.json must contain entities list.")

    def _upsert_entity_name(self, entities_config: dict, entity_name: str) -> None:
        entity_names = entities_config["entities"]
        if entity_name not in entity_names:
            entity_names.append(entity_name)
        self.updated_entities.append(entity_name)

    def _write_schema_file(self, entity_name: str, schema_definition: dict) -> None:
        schema_path = self.project_root / self.metadata_paths["entityMetadataRoot"] / entity_name / "schema.json"
        if schema_path.exists() and self.options.get("replaceExistingEntityFiles", True) is not True:
            raise ValueError(f"Schema file already exists and replaceExistingEntityFiles is false: {schema_path}")
        write_json_file(schema_path, schema_definition)
        self.updated_schema_files.append(self.to_project_relative_path(schema_path))

    def _write_seed_file(self, entity_name: str, seed_definition: dict) -> None:
        seed_path = self.project_root / self.metadata_paths["entityMetadataRoot"] / entity_name / "seed_data.json"
        if seed_path.exists() and self.options.get("replaceExistingEntityFiles", True) is not True:
            raise ValueError(f"Seed file already exists and replaceExistingEntityFiles is false: {seed_path}")
        write_json_file(seed_path, seed_definition)
        self.updated_seed_files.append(self.to_project_relative_path(seed_path))

    def _validate_schema_definition(self, entity_name: str, schema_definition: dict) -> None:
        columns = schema_definition.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema for '{entity_name}' must contain non-empty columns list.")
        column_names = []
        for column in columns:
            if not isinstance(column, dict):
                raise ValueError(f"Every column for '{entity_name}' must be an object.")
            column_name = self._get_required_string(column, "name", f"Every column for '{entity_name}' must contain name.")
            self._get_required_string(column, "type", f"Column '{column_name}' for '{entity_name}' must contain type.")
            if column_name in column_names:
                raise ValueError(f"Duplicate column '{column_name}' found for '{entity_name}'.")
            column_names.append(column_name)
        constraints = schema_definition.get("constraints", [])
        if not isinstance(constraints, list):
            raise ValueError(f"Schema constraints for '{entity_name}' must be a list when provided.")

    def _validate_seed_definition(self, entity_name: str, seed_definition: dict) -> None:
        table_name = self._get_required_string(seed_definition, "table", f"Seed data for '{entity_name}' must contain table.")
        if table_name != entity_name:
            raise ValueError(f"Seed data table '{table_name}' does not match entity name '{entity_name}'.")
        rows = seed_definition.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"Seed data for '{entity_name}' must contain rows list.")
        if rows:
            self._get_required_string(seed_definition, "conflictColumn", f"Seed data for '{entity_name}' must contain conflictColumn when rows exist.")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every seed row for '{entity_name}' must be an object.")

    def _run_validation(self) -> dict:
        script_path_value = self.validation.get("scriptPath")
        if not isinstance(script_path_value, str) or not script_path_value:
            raise ValueError("validation.scriptPath must be a non-empty string when validation is enabled.")

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
            "name": "validate_database_entity_definitions",
            "status": "PASSED" if completed.returncode == 0 else "FAILED",
            "scriptPath": self.to_project_relative_path(script_path),
            "durationSeconds": round(time.perf_counter() - started, 4),
            "returnCode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _build_report(self, status: str, started: float) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "prepare_postgres_entity_metadata"),
            "summary": {
                "status": status,
                "addedEntityCount": len(self.added_entity_names),
                "updatedEntityCount": len(self.updated_entities),
                "updatedSchemaFileCount": len(self.updated_schema_files),
                "updatedSeedFileCount": len(self.updated_seed_files),
                "durationSeconds": round(time.perf_counter() - started, 4),
            },
            "addedEntities": self.added_entity_names,
            "updatedEntities": self.updated_entities,
            "updatedSchemaFiles": self.updated_schema_files,
            "updatedSeedFiles": self.updated_seed_files,
            "validation": self.validation_result,
        }

    def _get_required_string(self, source: dict, key: str, error_message: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(error_message)
        return value


if __name__ == "__main__":
    AddPostgresEntityMetadataTask().run()
