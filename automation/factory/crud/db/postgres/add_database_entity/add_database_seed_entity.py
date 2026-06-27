"""
Updates PostgreSQL seed metadata from split CRUD seed configuration.

This script does not connect to PostgreSQL and does not insert database rows.
It updates metadata consumed by the existing PostgreSQL seed script.
"""

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
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file


class AddDatabaseSeedEntityScript(BaseScript):
    """Adds configured database seed groups to existing PostgreSQL seed metadata."""

    def __init__(self):
        super().__init__(__file__)
        self.metadata_paths = self._get_metadata_paths()
        self.options = self._get_options()
        self.allowed_entities = self._get_allowed_entities()
        self.seed_groups = self._get_seed_groups()
        self.updated_seed_groups = []

    def run(self) -> None:
        seed_config = self._read_metadata_file("seedConfigPath")
        self._validate_metadata_file(seed_config)

        for seed_group in self.seed_groups:
            table_name = self._get_required_string(
                seed_group,
                "table",
                "Every seed group must contain 'table'.",
            )
            self._validate_entity_is_listed(table_name)
            self._upsert_seed_group(
                seed_config=seed_config,
                entity_name=table_name,
                entity_seed=seed_group,
            )

        self._write_metadata_file("seedConfigPath", seed_config)

        report = self._build_report()
        self.write_json_report(report)
        self._print_success(report)

    def _get_metadata_paths(self) -> dict:
        metadata_paths = self.config.get("metadataPaths")

        if not isinstance(metadata_paths, dict):
            raise ValueError("Config must contain 'metadataPaths' object.")

        required_keys = [
            "databaseEntitiesPath",
            "seedConfigPath",
        ]

        for key in required_keys:
            value = metadata_paths.get(key)

            if not isinstance(value, str) or not value:
                raise ValueError(f"metadataPaths must contain non-empty '{key}'.")

        return metadata_paths

    def _get_options(self) -> dict:
        options = self.config.get("options", {})

        if not isinstance(options, dict):
            raise ValueError("Config 'options' must be an object when provided.")

        return options

    def _get_allowed_entities(self) -> list[str]:
        database_entities = self._read_metadata_file("databaseEntitiesPath")
        entities = database_entities.get("entities")

        if not isinstance(entities, list) or not entities:
            raise ValueError("database_entities.json must contain non-empty 'entities' list.")

        for entity_name in entities:
            if not isinstance(entity_name, str) or not entity_name:
                raise ValueError("Every database_entities.json entry must be a non-empty string.")

        if len(entities) != len(set(entities)):
            raise ValueError("database_entities.json must not contain duplicate entity names.")

        return entities

    def _get_seed_groups(self) -> list[dict]:
        seed_groups = self.config.get("seedGroups")

        if not isinstance(seed_groups, list):
            raise ValueError("Config must contain 'seedGroups' list.")

        for seed_group in seed_groups:
            if not isinstance(seed_group, dict):
                raise ValueError("Every seed group definition must be an object.")

        return seed_groups

    def _read_metadata_file(self, metadata_path_key: str) -> dict:
        return read_json_file(self._resolve_project_path(self.metadata_paths[metadata_path_key]))

    def _write_metadata_file(self, metadata_path_key: str, data: dict) -> None:
        write_json_file(
            self._resolve_project_path(self.metadata_paths[metadata_path_key]),
            data,
        )

    def _resolve_project_path(self, configured_path: str) -> Path:
        return self.project_root / configured_path

    def _validate_metadata_file(self, seed_config: dict) -> None:
        if not isinstance(seed_config.get("seedGroups"), list):
            raise ValueError("postgres_seed_data.json must contain 'seedGroups' list.")

    def _validate_entity_is_listed(self, entity_name: str) -> None:
        if entity_name not in self.allowed_entities:
            raise ValueError(
                f"Seed group '{entity_name}' is not listed in database_entities.json."
            )

    def _upsert_seed_group(
        self,
        seed_config: dict,
        entity_name: str,
        entity_seed: dict,
    ) -> None:
        self._validate_seed_group(entity_name, entity_seed)

        seed_groups = seed_config["seedGroups"]
        existing_index = self._find_seed_group_index(seed_groups, entity_name)
        replace_existing = self.options.get("replaceExistingSeedGroups", True)

        if existing_index is not None:
            if replace_existing is not True:
                raise ValueError(
                    f"Seed group '{entity_name}' already exists and replaceExistingSeedGroups is false."
                )

            seed_groups[existing_index] = entity_seed
        else:
            seed_groups.append(entity_seed)

        self.updated_seed_groups.append(entity_name)

    def _find_seed_group_index(
        self,
        seed_groups: list[dict],
        table_name: str,
    ) -> int | None:
        for index, seed_group in enumerate(seed_groups):
            if isinstance(seed_group, dict) and seed_group.get("table") == table_name:
                return index

        return None

    def _validate_seed_group(
        self,
        entity_name: str,
        seed_group: dict,
    ) -> None:
        table_name = self._get_required_string(
            seed_group,
            "table",
            f"Seed group for '{entity_name}' must contain 'table'.",
        )

        if table_name != entity_name:
            raise ValueError(
                f"Seed group table '{table_name}' does not match entity name '{entity_name}'."
            )

        self._get_required_string(
            seed_group,
            "conflictColumn",
            f"Seed group for '{entity_name}' must contain 'conflictColumn'.",
        )

        rows = seed_group.get("rows")

        if not isinstance(rows, list):
            raise ValueError(f"Seed group for '{entity_name}' must contain 'rows' list.")

        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Every seed row for '{entity_name}' must be an object.")

    def _get_required_string(
        self,
        source: dict,
        key: str,
        error_message: str,
    ) -> str:
        value = source.get(key)

        if not isinstance(value, str) or not value:
            raise ValueError(error_message)

        return value

    def _build_report(self) -> dict:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "update_postgres_seed_metadata"),
            "summary": {
                "status": "PASSED",
                "listedEntityCount": len(self.allowed_entities),
                "updatedSeedGroupCount": len(self.updated_seed_groups),
                "updatedSeedGroups": self.updated_seed_groups,
            },
            "metadataPaths": self.metadata_paths,
        }

    def _print_success(self, report: dict) -> None:
        summary = report["summary"]
        print_passed(
            "add_database_seed_entity: "
            f"{summary['updatedSeedGroupCount']} seed groups updated"
        )


def main() -> None:
    script = AddDatabaseSeedEntityScript()

    try:
        script.run()
    except Exception as exc:
        print_failed(f"add_database_seed_entity failed: {exc}")
        raise


if __name__ == "__main__":
    main()
