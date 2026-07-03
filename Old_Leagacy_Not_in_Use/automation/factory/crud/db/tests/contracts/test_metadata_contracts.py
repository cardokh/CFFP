"""Metadata contract tests for DB-root-local generic table metadata."""

from __future__ import annotations

from tests.support.db_json_validation import (
    assert_name,
    assert_schema_contract,
    assert_unique_strings,
    read_json,
)
from tests.support.db_test_paths import get_db_root


def test_database_metadata_points_to_postgres_implementation() -> None:
    db_root = get_db_root()
    database = read_json(db_root / "metadata" / "database.json")
    implementation = read_json(db_root / "implementations" / "postgres" / "database.json")

    assert database.get("currentImplementation") == "postgres"
    assert implementation.get("databaseType") == "postgres"


def test_active_metadata_modules_are_complete_and_in_sync() -> None:
    db_root = get_db_root()
    metadata_root = db_root / "metadata"
    modules_root = metadata_root / "modules"

    for module_root in sorted(path for path in modules_root.rglob("*") if (path / "tables.json").is_file()):
        table_root = module_root / "tables"
        table_names = assert_unique_strings(read_json(module_root / "tables.json").get("tables"), f"{module_root} tables")
        for table_name in table_names:
            assert_name(table_name, "table name")
            table_folder = table_root / table_name
            assert table_folder.is_dir(), f"Missing metadata folder for {table_name}."
            schema = assert_schema_contract(read_json(table_folder / "schema.json"), table_name)
            data = read_json(table_folder / "data.json")
            assert data.get("table") == table_name
            assert isinstance(data.get("rows"), list)

        physical_table_folders = sorted(path.name for path in table_root.iterdir() if path.is_dir()) if table_root.exists() else []
        assert physical_table_folders == sorted(table_names), f"{module_root}/tables folders must match tables.json exactly."


def test_active_foreign_key_dependencies_are_selected_in_same_metadata_scope() -> None:
    db_root = get_db_root()
    metadata_root = db_root / "metadata"
    modules_root = metadata_root / "modules"

    selected: set[str] = set()
    schemas: dict[str, dict] = {}
    for module_root in sorted(path for path in modules_root.rglob("*") if (path / "tables.json").is_file()):
        table_names = assert_unique_strings(read_json(module_root / "tables.json").get("tables"), f"{module_root} tables")
        selected.update(table_names)
        for table_name in table_names:
            schemas[table_name] = read_json(module_root / "tables" / table_name / "schema.json")

    missing_dependencies: list[str] = []
    for table_name, schema in schemas.items():
        for foreign_key in schema.get("foreignKeys", []):
            reference_table = foreign_key.get("references", {}).get("table")
            if reference_table not in selected:
                missing_dependencies.append(f"{table_name}->{reference_table}")

    assert not missing_dependencies, "Missing selected foreign key dependencies: " + ", ".join(missing_dependencies)
