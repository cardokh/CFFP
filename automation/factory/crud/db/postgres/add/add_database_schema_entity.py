"""Writes per-entity PostgreSQL schema metadata files and updates the entity selector."""

import sys
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


class AddDatabaseSchemaEntityScript(BaseScript):
    """Adds configured entity schema metadata under postgres/metadata/entities/<entity>/schema.json."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_metadata_paths()
        self.options = self._get_options()
        self.entities = self._get_entities()
        self.updated_entities = []
        self.updated_schema_files = []

    def run(self) -> None:
        entities_config = self._read_entities_config()
        self._validate_entities_config(entities_config)

        for entity in self.entities:
            entity_name = self._get_required_string(entity, "name", "Every entity must contain 'name'.")
            schema_definition = entity.get("schema")
            if not isinstance(schema_definition, dict):
                raise ValueError(f"Entity '{entity_name}' must contain 'schema' object.")
            self._validate_schema_definition(entity_name, schema_definition)
            self._upsert_entity_name(entities_config, entity_name)
            self._write_schema_file(entity_name, schema_definition)

        self._write_entities_config(entities_config)
        report = self._build_report()
        self.write_json_report(report)
        print_passed(
            f"add_database_schema_entity: {len(self.updated_entities)} entities, {len(self.updated_schema_files)} schema files updated"
        )

    def _get_metadata_paths(self) -> dict:
        metadata_paths = self.config.get("metadataPaths")
        if not isinstance(metadata_paths, dict):
            raise ValueError("Config must contain 'metadataPaths' object.")
        for key in ["entitiesConfigPath", "entityMetadataRoot"]:
            if not isinstance(metadata_paths.get(key), str) or not metadata_paths.get(key):
                raise ValueError(f"metadataPaths must contain non-empty '{key}'.")
        return metadata_paths

    def _get_options(self) -> dict:
        options = self.config.get("options", {})
        if not isinstance(options, dict):
            raise ValueError("Config options must be an object when provided.")
        return options

    def _get_entities(self) -> list[dict]:
        entities = self.config.get("entities")
        if not isinstance(entities, list):
            raise ValueError("Config must contain 'entities' list.")
        for entity in entities:
            if not isinstance(entity, dict):
                raise ValueError("Every entity definition must be an object.")
        return entities

    def _read_entities_config(self) -> dict:
        return read_json_file(self.project_root / self.metadata_paths["entitiesConfigPath"])

    def _write_entities_config(self, entities_config: dict) -> None:
        write_json_file(self.project_root / self.metadata_paths["entitiesConfigPath"], entities_config)

    def _validate_entities_config(self, entities_config: dict) -> None:
        if not isinstance(entities_config.get("entities"), list):
            raise ValueError("entities.json must contain 'entities' list.")

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

    def _validate_schema_definition(self, entity_name: str, schema_definition: dict) -> None:
        columns = schema_definition.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema for '{entity_name}' must contain non-empty 'columns' list.")
        column_names = []
        for column in columns:
            if not isinstance(column, dict):
                raise ValueError(f"Every column for '{entity_name}' must be an object.")
            column_name = self._get_required_string(column, "name", f"Every column for '{entity_name}' must contain 'name'.")
            self._get_required_string(column, "type", f"Column '{column_name}' for '{entity_name}' must contain 'type'.")
            if column_name in column_names:
                raise ValueError(f"Duplicate column '{column_name}' found for '{entity_name}'.")
            column_names.append(column_name)
        constraints = schema_definition.get("constraints", [])
        if not isinstance(constraints, list):
            raise ValueError(f"Schema constraints for '{entity_name}' must be a list when provided.")

    def _get_required_string(self, source: dict, key: str, error_message: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(error_message)
        return value

    def _build_report(self) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "write_postgres_entity_schema_metadata"),
            "summary": {
                "status": "PASSED",
                "updatedEntityCount": len(self.updated_entities),
                "updatedSchemaFileCount": len(self.updated_schema_files),
            },
            "updatedEntities": self.updated_entities,
            "updatedSchemaFiles": self.updated_schema_files,
        }


if __name__ == "__main__":
    AddDatabaseSchemaEntityScript().run()
