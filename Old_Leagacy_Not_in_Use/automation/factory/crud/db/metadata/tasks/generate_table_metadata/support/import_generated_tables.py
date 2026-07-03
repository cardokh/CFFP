"""Stage 2 deterministic import for generated table batches."""

from pathlib import Path
from typing import Any

from .generated_tables_loader import load_generated_tables
from .metadata_validator import validate_generated_tables_batch
from .metadata_writer import read_existing_table_names, write_generated_tables


def import_generated_tables(db_root: Path, script_directory: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Read, validate, and import generated metadata table batches."""

    generated_tables_paths = _read_generated_tables_paths(script_directory, config)
    target_metadata_root = _resolve_db_path(db_root, config, "targetMetadataRoot")
    target_module = config.get("targetModule", "ccore/automation")
    if not isinstance(target_module, str) or not target_module:
        raise ValueError("Config must contain non-empty 'targetModule'.")

    module_root = target_metadata_root / "modules" / target_module
    existing_tables = read_existing_table_names(module_root)
    imported_tables: list[str] = []
    imported_batches: list[dict[str, Any]] = []

    for generated_tables_path in generated_tables_paths:
        batch = load_generated_tables(generated_tables_path)
        tables = batch["tables"]

        print(f"{len(tables)} tables found in {_to_script_relative_path(script_directory, generated_tables_path)}.")
        validate_generated_tables_batch(batch, existing_tables + imported_tables)

        if not tables:
            imported_batches.append(
                {
                    "status": "PASSED",
                    "generatedTablesPath": _to_script_relative_path(script_directory, generated_tables_path),
                    "foundTableCount": 0,
                    "importedTableCount": 0,
                    "importedTables": [],
                }
            )
            continue

        batch_imported_tables = write_generated_tables(module_root, tables)
        imported_tables.extend(batch_imported_tables)
        imported_batches.append(
            {
                "status": "PASSED",
                "generatedTablesPath": _to_script_relative_path(script_directory, generated_tables_path),
                "foundTableCount": len(tables),
                "importedTableCount": len(batch_imported_tables),
                "importedTables": batch_imported_tables,
            }
        )
        print(f"Imported {len(batch_imported_tables)} tables.")

    if not imported_tables:
        print("Nothing to import.")

    return {
        "status": "PASSED",
        "targetModule": target_module,
        "batchCount": len(imported_batches),
        "foundTableCount": sum(batch["foundTableCount"] for batch in imported_batches),
        "importedTableCount": len(imported_tables),
        "importedTables": imported_tables,
        "batches": imported_batches,
    }


def _read_generated_tables_paths(script_directory: Path, config: dict[str, Any]) -> list[Path]:
    specification_entries = config.get("architectureSpecifications")
    if isinstance(specification_entries, list) and specification_entries:
        paths: list[Path] = []
        for index, entry in enumerate(specification_entries):
            if isinstance(entry, str):
                generated_tables_path = _default_generated_tables_path(entry)
            elif isinstance(entry, dict):
                generated_tables_path = entry.get("generatedTablesPath")
                if not isinstance(generated_tables_path, str) or not generated_tables_path:
                    raise ValueError(
                        f"Architecture specification entry at index {index} must contain non-empty "
                        "'generatedTablesPath'."
                    )
            else:
                raise ValueError(f"Architecture specification entry at index {index} must be an object or string.")
            paths.append(_resolve_script_path(script_directory, generated_tables_path))
        return paths

    legacy_generated_tables_path = config.get("generatedTablesPath")
    if isinstance(legacy_generated_tables_path, str) and legacy_generated_tables_path:
        return [_resolve_script_path(script_directory, legacy_generated_tables_path)]

    raise ValueError("Config must contain architectureSpecifications or generatedTablesPath.")


def _default_generated_tables_path(specification_path: str) -> str:
    path = Path(specification_path)
    generated_name = path.name.replace("architecture_specification_", "generated_tables_")
    if generated_name == path.name:
        generated_name = f"generated_tables_{path.stem}.json"
    parts = list(path.parts)
    if "specifications" in parts:
        parts[parts.index("specifications")] = "generated"
        parts[-1] = generated_name
        return Path(*parts).as_posix()
    return (Path("input") / "generated" / generated_name).as_posix()


def _resolve_script_path(script_directory: Path, configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return script_directory / path


def _resolve_db_path(db_root: Path, config: dict[str, Any], config_key: str) -> Path:
    configured_path = config.get(config_key)
    if not isinstance(configured_path, str) or not configured_path:
        raise ValueError(f"Config must contain non-empty '{config_key}'.")
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return db_root / path


def _to_script_relative_path(script_directory: Path, path: Path) -> str:
    try:
        return path.relative_to(script_directory).as_posix()
    except ValueError:
        return str(path)
