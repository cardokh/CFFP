"""Writes per-entity PostgreSQL seed metadata files."""

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


class AddDatabaseSeedEntityScript(BaseScript):
    """Adds configured seed metadata under postgres/metadata/entities/<entity>/seed_data.json."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_metadata_paths()
        self.options = self._get_options()
        self.allowed_entities = self._get_allowed_entities()
        self.seed_groups = self._get_seed_groups()
        self.updated_seed_files = []

    def run(self) -> None:
        for seed_group in self.seed_groups:
            table_name = self._get_required_string(seed_group, "table", "Every seed group must contain 'table'.")
            self._validate_entity_is_listed(table_name)
            self._validate_seed_group(table_name, seed_group)
            self._write_seed_file(table_name, seed_group)

        report = self._build_report()
        self.write_json_report(report)
        print_passed(f"add_database_seed_entity: {len(self.updated_seed_files)} seed files updated")

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

    def _get_allowed_entities(self) -> list[str]:
        entities_config = read_json_file(self.project_root / self.metadata_paths["entitiesConfigPath"])
        entities = entities_config.get("entities")
        if not isinstance(entities, list) or not entities:
            raise ValueError("entities.json must contain non-empty 'entities' list.")
        return entities

    def _get_seed_groups(self) -> list[dict]:
        seed_groups = self.config.get("seedGroups")
        if not isinstance(seed_groups, list):
            raise ValueError("Config must contain 'seedGroups' list.")
        for seed_group in seed_groups:
            if not isinstance(seed_group, dict):
                raise ValueError("Every seed group definition must be an object.")
        return seed_groups

    def _validate_entity_is_listed(self, entity_name: str) -> None:
        if entity_name not in self.allowed_entities:
            raise ValueError(f"Seed group '{entity_name}' is not listed in entities.json.")

    def _write_seed_file(self, entity_name: str, seed_group: dict) -> None:
        seed_path = self.project_root / self.metadata_paths["entityMetadataRoot"] / entity_name / "seed_data.json"
        if seed_path.exists() and self.options.get("replaceExistingEntityFiles", True) is not True:
            raise ValueError(f"Seed file already exists and replaceExistingEntityFiles is false: {seed_path}")
        write_json_file(seed_path, seed_group)
        self.updated_seed_files.append(self.to_project_relative_path(seed_path))

    def _validate_seed_group(self, entity_name: str, seed_group: dict) -> None:
        table_name = self._get_required_string(seed_group, "table", f"Seed group for '{entity_name}' must contain 'table'.")
        if table_name != entity_name:
            raise ValueError(f"Seed group table '{table_name}' does not match entity name '{entity_name}'.")
        rows = seed_group.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"Seed group for '{entity_name}' must contain 'rows' list.")
        if rows:
            self._get_required_string(seed_group, "conflictColumn", f"Seed group for '{entity_name}' must contain 'conflictColumn'.")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every seed row for '{entity_name}' must be an object.")

    def _get_required_string(self, source: dict, key: str, error_message: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(error_message)
        return value

    def _build_report(self) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "write_postgres_entity_seed_metadata"),
            "summary": {"status": "PASSED", "updatedSeedFileCount": len(self.updated_seed_files)},
            "updatedSeedFiles": self.updated_seed_files,
        }


if __name__ == "__main__":
    AddDatabaseSeedEntityScript().run()
