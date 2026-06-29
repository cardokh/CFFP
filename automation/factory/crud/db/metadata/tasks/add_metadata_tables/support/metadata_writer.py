"""Writes imported generated tables into generic metadata."""

from pathlib import Path
from typing import Any

from scripts.shared.script_json_utils import read_json_file, write_json_file


def read_existing_table_names(module_root: Path) -> list[str]:
    """Read the module table registry if it exists."""

    registry_path = module_root / "tables.json"
    if not registry_path.exists():
        return []
    registry = read_json_file(registry_path)
    tables = registry.get("tables", [])
    if not isinstance(tables, list):
        raise ValueError(f"Invalid tables registry: {registry_path}")
    return [str(table_name) for table_name in tables]


def write_generated_tables(module_root: Path, tables: list[dict[str, Any]]) -> list[str]:
    """Write schema/data files and update tables.json for imported tables."""

    imported_table_names: list[str] = []
    for table in tables:
        table_name = table["name"]
        table_root = module_root / "tables" / table_name
        table_root.mkdir(parents=True, exist_ok=True)
        write_json_file(table_root / "schema.json", table.get("schema", {"name": table_name}))
        write_json_file(table_root / "data.json", table.get("data", {"table": table_name, "rows": []}))
        imported_table_names.append(table_name)

    if imported_table_names:
        existing_table_names = read_existing_table_names(module_root)
        merged_table_names = sorted(set(existing_table_names) | set(imported_table_names))
        write_json_file(module_root / "tables.json", {"tables": merged_table_names})

    return imported_table_names
