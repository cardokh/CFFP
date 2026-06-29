"""Stage 2 deterministic import for generated table batches."""

from pathlib import Path
from typing import Any

from .generated_tables_loader import load_generated_tables
from .metadata_validator import validate_generated_tables_batch
from .metadata_writer import read_existing_table_names, write_generated_tables


def import_generated_tables(project_root: Path, script_directory: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Read, validate, and import generated metadata tables."""

    generated_tables_path = _resolve_script_path(script_directory, config, "generatedTablesPath")
    target_metadata_root = _resolve_project_path(project_root, config, "targetMetadataRoot")
    target_module = config.get("targetModule", "ccore/automation")
    if not isinstance(target_module, str) or not target_module:
        raise ValueError("Config must contain non-empty 'targetModule'.")

    module_root = target_metadata_root / "modules" / target_module
    batch = load_generated_tables(generated_tables_path)
    tables = batch["tables"]

    print(f"{len(tables)} tables found.")
    existing_tables = read_existing_table_names(module_root)
    validate_generated_tables_batch(batch, existing_tables)

    if not tables:
        print("Nothing to import.")
        return {
            "status": "PASSED",
            "generatedTablesPath": str(generated_tables_path),
            "targetModule": target_module,
            "foundTableCount": 0,
            "importedTableCount": 0,
            "importedTables": [],
        }

    imported_tables = write_generated_tables(module_root, tables)
    print(f"Imported {len(imported_tables)} tables.")
    return {
        "status": "PASSED",
        "generatedTablesPath": str(generated_tables_path),
        "targetModule": target_module,
        "foundTableCount": len(tables),
        "importedTableCount": len(imported_tables),
        "importedTables": imported_tables,
    }


def _resolve_script_path(script_directory: Path, config: dict[str, Any], config_key: str) -> Path:
    configured_path = config.get(config_key)
    if not isinstance(configured_path, str) or not configured_path:
        raise ValueError(f"Config must contain non-empty '{config_key}'.")
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return script_directory / path


def _resolve_project_path(project_root: Path, config: dict[str, Any], config_key: str) -> Path:
    configured_path = config.get(config_key)
    if not isinstance(configured_path, str) or not configured_path:
        raise ValueError(f"Config must contain non-empty '{config_key}'.")
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return project_root / path
