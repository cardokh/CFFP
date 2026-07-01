"""Stage 1 generator for table batches from architecture specifications."""

from copy import deepcopy
from pathlib import Path
from typing import Any

from scripts.shared.script_json_utils import read_json_file, write_json_file
from db_path_utils import get_application_stage_root


_ARCHITECTURE_SPECIFICATIONS_CONFIG_KEY = "architectureSpecifications"


def generate_generated_tables(db_root: Path, script_directory: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Read architecture specifications and write generated table batch files."""

    specification_entries = _read_specification_entries(config)
    generated_results: list[dict[str, Any]] = []
    total_table_count = 0
    all_table_names: list[str] = []

    for entry in specification_entries:
        architecture_specification_path = _resolve_application_stage_path(db_root, config, entry["path"])
        generated_tables_path = _resolve_application_stage_path(db_root, config, entry["generatedTablesPath"])

        specification = _read_architecture_specification(architecture_specification_path)
        tables = _build_generated_tables(specification)
        batch = {
            "source": {
                "type": "architectureSpecification",
                "name": specification.get("name"),
                "version": specification.get("version"),
                "path": _to_application_stage_relative_path(db_root, config, architecture_specification_path),
            },
            "targetModule": specification.get("targetModule", config.get("targetModule", "ccore/automation")),
            "tables": tables,
        }

        generated_tables_path.parent.mkdir(parents=True, exist_ok=True)
        write_json_file(generated_tables_path, batch)

        table_names = [table["name"] for table in tables]
        total_table_count += len(tables)
        all_table_names.extend(table_names)
        generated_results.append(
            {
                "name": entry.get("name"),
                "architectureSpecificationPath": _to_application_stage_relative_path(db_root, config, architecture_specification_path),
                "generatedTablesPath": _to_application_stage_relative_path(db_root, config, generated_tables_path),
                "tableCount": len(tables),
                "tables": table_names,
            }
        )
        print(
            f"Generated {len(tables)} table(s) from "
            f"{_to_application_stage_relative_path(db_root, config, architecture_specification_path)}."
        )

    return {
        "status": "PASSED",
        "mode": "architecture_specifications",
        "processedSpecificationCount": len(generated_results),
        "tableCount": total_table_count,
        "tables": all_table_names,
        "specifications": generated_results,
    }


def _read_specification_entries(config: dict[str, Any]) -> list[dict[str, str]]:
    entries = config.get(_ARCHITECTURE_SPECIFICATIONS_CONFIG_KEY)
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"Config must contain non-empty '{_ARCHITECTURE_SPECIFICATIONS_CONFIG_KEY}' list.")

    normalized_entries: list[dict[str, str]] = []
    for index, entry in enumerate(entries):
        if isinstance(entry, str):
            path = entry
            generated_tables_path = _default_generated_tables_path(path)
            normalized_entries.append(
                {
                    "name": Path(path).stem,
                    "path": path,
                    "generatedTablesPath": generated_tables_path,
                }
            )
            continue

        if not isinstance(entry, dict):
            raise ValueError(f"Architecture specification entry at index {index} must be an object or string.")
        path = entry.get("path")
        generated_tables_path = entry.get("generatedTablesPath")
        if not isinstance(path, str) or not path:
            raise ValueError(f"Architecture specification entry at index {index} must contain non-empty 'path'.")
        if not isinstance(generated_tables_path, str) or not generated_tables_path:
            raise ValueError(
                f"Architecture specification entry at index {index} must contain non-empty 'generatedTablesPath'."
            )
        normalized_entries.append(
            {
                "name": str(entry.get("name", Path(path).stem)),
                "path": path,
                "generatedTablesPath": generated_tables_path,
            }
        )

    return normalized_entries


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


def _resolve_application_stage_path(db_root: Path, config: dict[str, Any], configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return get_application_stage_root(db_root, config) / path


def _read_architecture_specification(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Architecture specification not found: {path}")
    specification = read_json_file(path)
    if not isinstance(specification, dict):
        raise ValueError("Architecture specification must contain a JSON object.")
    tables = specification.get("tables")
    if not isinstance(tables, list):
        raise ValueError("Architecture specification must contain a 'tables' list.")
    return specification


def _build_generated_tables(specification: dict[str, Any]) -> list[dict[str, Any]]:
    generated_tables: list[dict[str, Any]] = []
    for table in specification["tables"]:
        if not isinstance(table, dict):
            raise ValueError("Every architecture specification table must be an object.")
        table_name = _get_required_string(table, "name", "Every architecture specification table must contain name.")
        schema = deepcopy(table.get("schema"))
        data = deepcopy(table.get("data", {"table": table_name, "rows": []}))
        if not isinstance(schema, dict):
            raise ValueError(f"Architecture specification table '{table_name}' must contain schema object.")
        if not isinstance(data, dict):
            raise ValueError(f"Architecture specification table '{table_name}' data must be an object when provided.")
        if schema.get("name") != table_name:
            raise ValueError(f"Architecture specification schema name must match table '{table_name}'.")
        if data.get("table") != table_name:
            raise ValueError(f"Architecture specification data table must match table '{table_name}'.")
        generated_tables.append(
            {
                "name": table_name,
                "schema": schema,
                "data": data,
            }
        )
    return generated_tables


def _get_required_string(source: dict[str, Any], key: str, error_message: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(error_message)
    return value


def _resolve_script_path(script_directory: Path, configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return script_directory / path


def _to_script_relative_path(script_directory: Path, path: Path) -> str:
    try:
        return path.relative_to(script_directory).as_posix()
    except ValueError:
        return str(path)


def _to_application_stage_relative_path(db_root: Path, config: dict[str, Any], path: Path) -> str:
    try:
        return path.resolve().relative_to(get_application_stage_root(db_root, config).resolve()).as_posix()
    except ValueError:
        return str(path)
