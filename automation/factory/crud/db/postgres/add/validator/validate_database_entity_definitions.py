"""Validates per-entity PostgreSQL schema and seed metadata files."""

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
from scripts.shared.script_json_utils import read_json_file


class ValidateDatabaseEntityDefinitionsScript(BaseScript):
    """Validates selected entity metadata under postgres/metadata/entities."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_metadata_paths()
        self.entity_metadata_root = self.project_root / self.metadata_paths["entityMetadataRoot"]
        self.entities_config = read_json_file(self.project_root / self.metadata_paths["entitiesConfigPath"])
        self.checks = []

    def run(self) -> None:
        entity_names = self._get_entity_names()
        self._validate_unique_entities(entity_names)

        for entity_name in entity_names:
            self._validate_entity_folder(entity_name)

        report = self._build_report(entity_names)
        self.write_json_report(report)
        print_passed(f"validate_database_entity_definitions: {len(self.checks)} checks passed")

    def _get_metadata_paths(self) -> dict:
        metadata_paths = self.config.get("metadataPaths")
        if not isinstance(metadata_paths, dict):
            raise ValueError("Config must contain 'metadataPaths' object.")
        for key in ["entitiesConfigPath", "entityMetadataRoot"]:
            if not isinstance(metadata_paths.get(key), str) or not metadata_paths.get(key):
                raise ValueError(f"metadataPaths must contain non-empty '{key}'.")
        return metadata_paths

    def _get_entity_names(self) -> list[str]:
        entities = self.entities_config.get("entities")
        if not isinstance(entities, list) or not entities:
            raise ValueError("entities.json must contain non-empty 'entities'.")
        for entity_name in entities:
            if not isinstance(entity_name, str) or not entity_name:
                raise ValueError("Every entities.json entry must be a non-empty string.")
        self.checks.append("entities.json contains non-empty entity list")
        return entities

    def _validate_unique_entities(self, entity_names: list[str]) -> None:
        if len(entity_names) != len(set(entity_names)):
            raise ValueError("entities.json must not contain duplicate entity names.")
        self.checks.append("entities.json contains unique entity names")

    def _validate_entity_folder(self, entity_name: str) -> None:
        entity_folder = self.entity_metadata_root / entity_name
        schema_path = entity_folder / "schema.json"
        seed_path = entity_folder / "seed_data.json"

        if not entity_folder.is_dir():
            raise ValueError(f"Missing entity metadata folder: {entity_folder}")
        if not schema_path.exists():
            raise ValueError(f"Missing schema metadata: {schema_path}")
        if not seed_path.exists():
            raise ValueError(f"Missing seed metadata: {seed_path}")

        schema = read_json_file(schema_path)
        seed = read_json_file(seed_path)
        self._validate_schema(entity_name, schema)
        self._validate_seed(entity_name, seed)
        self.checks.append(f"{entity_name} contains schema.json and seed_data.json")

    def _validate_schema(self, entity_name: str, schema: dict) -> None:
        if not isinstance(schema, dict):
            raise ValueError(f"Schema for '{entity_name}' must be an object.")
        columns = schema.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Schema for '{entity_name}' must contain non-empty columns list.")
        column_names = []
        for column in columns:
            if not isinstance(column, dict):
                raise ValueError(f"Every column for '{entity_name}' must be an object.")
            column_name = column.get("name")
            if not isinstance(column_name, str) or not column_name:
                raise ValueError(f"Every column for '{entity_name}' must contain non-empty name.")
            if not isinstance(column.get("type"), str) or not column.get("type"):
                raise ValueError(f"Column '{column_name}' for '{entity_name}' must contain non-empty type.")
            if column_name in column_names:
                raise ValueError(f"Duplicate column '{column_name}' found for '{entity_name}'.")
            column_names.append(column_name)
        constraints = schema.get("constraints", [])
        if not isinstance(constraints, list):
            raise ValueError(f"Schema constraints for '{entity_name}' must be a list when provided.")

    def _validate_seed(self, entity_name: str, seed: dict) -> None:
        if not isinstance(seed, dict):
            raise ValueError(f"Seed metadata for '{entity_name}' must be an object.")
        if seed.get("table") != entity_name:
            raise ValueError(f"Seed metadata table must match entity name '{entity_name}'.")
        rows = seed.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"Seed metadata for '{entity_name}' must contain rows list.")
        if rows and (not isinstance(seed.get("conflictColumn"), str) or not seed.get("conflictColumn")):
            raise ValueError(f"Seed metadata for '{entity_name}' must contain conflictColumn when rows are present.")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every seed row for '{entity_name}' must be an object.")

    def _build_report(self, entity_names: list[str]) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "validate_postgres_entity_metadata_files"),
            "summary": {
                "status": "PASSED",
                "selectedEntityCount": len(entity_names),
                "checkCount": len(self.checks),
            },
            "entities": entity_names,
            "checks": self.checks,
        }


if __name__ == "__main__":
    ValidateDatabaseEntityDefinitionsScript().run()
