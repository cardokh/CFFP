"""Stage 1 generator for table batches from an architecture specification."""

from copy import deepcopy
from pathlib import Path
from typing import Any

from scripts.shared.script_json_utils import read_json_file, write_json_file


_ARCHITECTURE_SPECIFICATION_PATH_CONFIG_KEY = "architectureSpecificationPath"
_GENERATED_TABLES_PATH_CONFIG_KEY = "generatedTablesPath"


def generate_generated_tables(script_directory: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Read the architecture specification and write generated_tables.json."""

    architecture_specification_path = _resolve_script_path(
        script_directory,
        config,
        _ARCHITECTURE_SPECIFICATION_PATH_CONFIG_KEY,
    )
    generated_tables_path = _resolve_script_path(
        script_directory,
        config,
        _GENERATED_TABLES_PATH_CONFIG_KEY,
    )

    specification = _read_architecture_specification(architecture_specification_path)
    tables = _build_generated_tables(specification)
    batch = {
        "source": {
            "type": "architectureSpecification",
            "name": specification.get("name"),
            "version": specification.get("version"),
            "path": _to_script_relative_path(script_directory, architecture_specification_path),
        },
        "targetModule": specification.get("targetModule", config.get("targetModule", "ccore/automation")),
        "tables": tables,
    }

    write_json_file(generated_tables_path, batch)
    print(f"Generated {len(tables)} table(s) from architecture specification.")
    return {
        "status": "PASSED",
        "mode": "architecture_specification",
        "architectureSpecificationPath": _to_script_relative_path(script_directory, architecture_specification_path),
        "generatedTablesPath": _to_script_relative_path(script_directory, generated_tables_path),
        "tableCount": len(tables),
        "tables": [table["name"] for table in tables],
    }


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
        generated_tables.append({
            "name": table_name,
            "schema": schema,
            "data": data,
        })
    return generated_tables


def _get_required_string(source: dict[str, Any], key: str, error_message: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(error_message)
    return value


def _resolve_script_path(script_directory: Path, config: dict[str, Any], config_key: str) -> Path:
    configured_path = config.get(config_key)
    if not isinstance(configured_path, str) or not configured_path:
        raise ValueError(f"Config must contain non-empty '{config_key}'.")
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return script_directory / path


def _to_script_relative_path(script_directory: Path, path: Path) -> str:
    try:
        return path.relative_to(script_directory).as_posix()
    except ValueError:
        return str(path)
