"""Remove table metadata from the generic database-neutral metadata model."""

import shutil
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
from scripts.shared.script_json_utils import read_json_file, write_json_file
from db_path_utils import get_db_root, resolve_application_stage_config_path, to_application_stage_relative_path


class RemoveMetadataTablesScript(BaseScript):
    """Remove one or more table metadata definitions from a metadata module."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.db_root = get_db_root(__file__)

    def run(self) -> None:
        started = time.perf_counter()
        try:
            result = remove_metadata_tables(self.db_root, self.config)
            report = {
                "scriptName": self.script_name,
                "summary": {
                    "status": "PASSED",
                    "elapsedSeconds": round(time.perf_counter() - started, 3),
                    "requestedTableCount": len(result["requestedTables"]),
                    "removedTableCount": len(result["removedTables"]),
                    "missingTableCount": len(result["missingTables"]),
                },
                "removal": result,
            }
            self.write_json_report(report)
            print_passed(
                f"{self.script_name}: removed {len(result['removedTables'])} table(s), "
                f"missing {len(result['missingTables'])}"
            )
        except Exception as error:
            report = {
                "scriptName": self.script_name,
                "summary": {
                    "status": "FAILED",
                    "elapsedSeconds": round(time.perf_counter() - started, 3),
                    "error": str(error),
                },
            }
            self.write_json_report(report)
            print_failed(f"{self.script_name}: {error}")
            raise


def remove_metadata_tables(db_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Remove configured table metadata folders and registry entries."""

    target_metadata_root = resolve_application_stage_config_path(db_root, config, "targetMetadataRoot")
    target_module = _get_required_string(config, "targetModule")
    requested_tables = _get_requested_tables(config)

    module_root = target_metadata_root / "modules" / target_module
    tables_registry_path = module_root / "tables.json"
    tables_root = module_root / "tables"

    if not module_root.exists():
        raise ValueError(f"Target metadata module does not exist: {module_root}")
    if not tables_registry_path.exists():
        raise ValueError(f"Target metadata registry does not exist: {tables_registry_path}")

    registry = read_json_file(tables_registry_path)
    registry_tables = registry.get("tables")
    if not isinstance(registry_tables, list):
        raise ValueError(f"Invalid tables registry: {tables_registry_path}")

    existing_table_names = [str(table_name) for table_name in registry_tables]
    requested_table_set = set(requested_tables)

    updated_table_names = [
        table_name
        for table_name in existing_table_names
        if table_name not in requested_table_set
    ]

    removed_tables: list[str] = []
    missing_tables: list[str] = []
    removed_folders: list[str] = []
    missing_folders: list[str] = []

    for table_name in requested_tables:
        table_folder = tables_root / table_name
        table_registered = table_name in existing_table_names
        folder_exists = table_folder.exists()

        if table_registered or folder_exists:
            removed_tables.append(table_name)
        else:
            missing_tables.append(table_name)

        if folder_exists:
            if not table_folder.is_dir():
                raise ValueError(f"Table metadata path is not a folder: {table_folder}")
            shutil.rmtree(table_folder)
            removed_folders.append(to_application_stage_relative_path(db_root, config, table_folder))
        else:
            missing_folders.append(to_application_stage_relative_path(db_root, config, table_folder))

    if updated_table_names != existing_table_names:
        write_json_file(tables_registry_path, {"tables": updated_table_names})

    return {
        "status": "PASSED",
        "targetMetadataRoot": to_application_stage_relative_path(db_root, config, target_metadata_root),
        "targetModule": target_module,
        "tablesRegistryPath": to_application_stage_relative_path(db_root, config, tables_registry_path),
        "requestedTables": requested_tables,
        "removedTables": removed_tables,
        "missingTables": missing_tables,
        "removedFolders": removed_folders,
        "missingFolders": missing_folders,
        "remainingTableCount": len(updated_table_names),
    }


def _get_requested_tables(config: dict[str, Any]) -> list[str]:
    tables = config.get("tables")
    if not isinstance(tables, list):
        raise ValueError("Config must contain a 'tables' list.")
    if not tables:
        raise ValueError("Config 'tables' must contain at least one table name.")

    requested_tables: list[str] = []
    for table in tables:
        if not isinstance(table, str) or not table.strip():
            raise ValueError("Every configured table name must be a non-empty string.")
        table_name = table.strip()
        _validate_table_name(table_name)
        requested_tables.append(table_name)

    duplicates = sorted({table for table in requested_tables if requested_tables.count(table) > 1})
    if duplicates:
        raise ValueError(f"Duplicate table names configured for removal: {duplicates}")

    return requested_tables


def _validate_table_name(table_name: str) -> None:
    allowed_characters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
    if any(character not in allowed_characters for character in table_name):
        raise ValueError(f"Invalid table name configured for removal: {table_name}")
    if table_name in {".", ".."}:
        raise ValueError(f"Invalid table name configured for removal: {table_name}")


def _get_required_string(config: dict[str, Any], config_key: str) -> str:
    value = config.get(config_key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Config must contain non-empty '{config_key}'.")
    return value



if __name__ == "__main__":
    RemoveMetadataTablesScript().run()
