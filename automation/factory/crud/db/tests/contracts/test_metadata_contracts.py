"""Metadata contract tests for new, promoted, and active PostgreSQL table metadata."""

from __future__ import annotations

from automation.factory.crud.db.tests.support.db_json_validation import (
    assert_name,
    assert_schema_contract,
    assert_seed_contract,
    assert_unique_strings,
    read_json,
)
from automation.factory.crud.db.tests.support.db_test_paths import get_postgres_root


def test_new_tables_json_is_valid_and_backed_by_staged_metadata() -> None:
    postgres_root = get_postgres_root()
    new_tables_path = postgres_root / "generate_table_metadata" / "metadata" / "new_tables.json"
    added_entities_path = postgres_root / "promote_db_metadata" / "metadata" / "added_entities.json"
    staged_root = postgres_root / "promote_db_metadata" / "metadata" / "entities"

    new_tables = read_json(new_tables_path)
    table_entries = new_tables.get("tables")
    assert isinstance(table_entries, list), "new_tables.json must contain tables list."
    table_names: list[str] = []
    for entry in table_entries:
        if isinstance(entry, str):
            table_name = assert_name(entry, "new_tables table name")
        else:
            assert isinstance(entry, dict), "new_tables entries must be strings or objects."
            table_name = assert_name(entry.get("table"), "new_tables table definition table")
        assert table_name not in table_names, f"Duplicate table in new_tables.json: {table_name}"
        table_names.append(table_name)

    added_entities = assert_unique_strings(read_json(added_entities_path).get("entities"), "added_entities.json entities")
    for table_name in table_names:
        assert table_name in added_entities, f"{table_name} must be registered in added_entities.json."
        assert (staged_root / table_name / "schema.json").is_file(), f"Missing staged schema for {table_name}."
        assert (staged_root / table_name / "seed_data.json").is_file(), f"Missing staged seed data for {table_name}."


def test_active_metadata_files_are_complete_and_in_sync() -> None:
    postgres_root = get_postgres_root()
    metadata_root = postgres_root / "metadata"
    entity_root = metadata_root / "entities"

    database = read_json(metadata_root / "database.json")
    assert database.get("databaseType") == "postgres"
    assert isinstance(database.get("applicationConnection"), dict)
    assert isinstance(database["applicationConnection"].get("databaseName"), str)

    entity_names = assert_unique_strings(read_json(metadata_root / "entities.json").get("entities"), "entities.json entities")
    for entity_name in entity_names:
        assert_name(entity_name, "entity name")
        entity_folder = entity_root / entity_name
        assert entity_folder.is_dir(), f"Missing active metadata folder for {entity_name}."
        schema = assert_schema_contract(read_json(entity_folder / "schema.json"), entity_name)
        assert_seed_contract(read_json(entity_folder / "seed_data.json"), entity_name, schema)

    physical_entity_folders = sorted(path.name for path in entity_root.iterdir() if path.is_dir())
    assert physical_entity_folders == sorted(entity_names), "metadata/entities folders must match entities.json exactly."


def test_promoted_metadata_files_are_complete_and_in_sync() -> None:
    postgres_root = get_postgres_root()
    promoted_root = postgres_root / "promote_db_metadata" / "metadata"
    staged_entity_root = promoted_root / "entities"

    entity_names = assert_unique_strings(read_json(promoted_root / "added_entities.json").get("entities"), "added_entities.json entities")
    for entity_name in entity_names:
        assert_name(entity_name, "promoted entity name")
        entity_folder = staged_entity_root / entity_name
        assert entity_folder.is_dir(), f"Missing promoted metadata folder for {entity_name}."
        schema = assert_schema_contract(read_json(entity_folder / "schema.json"), entity_name)
        assert_seed_contract(read_json(entity_folder / "seed_data.json"), entity_name, schema)

    physical_entity_folders = sorted(path.name for path in staged_entity_root.iterdir() if path.is_dir())
    assert physical_entity_folders == sorted(entity_names), "promote_db_metadata/metadata/entities must match added_entities.json exactly."


def test_active_foreign_key_dependencies_are_selected() -> None:
    postgres_root = get_postgres_root()
    metadata_root = postgres_root / "metadata"
    entity_root = metadata_root / "entities"
    entity_names = assert_unique_strings(read_json(metadata_root / "entities.json").get("entities"), "entities.json entities")
    selected = set(entity_names)

    missing_dependencies: list[str] = []
    for entity_name in entity_names:
        schema = read_json(entity_root / entity_name / "schema.json")
        for constraint in schema.get("constraints", []):
            if constraint.get("type") != "foreignKey":
                continue
            reference_table = constraint["references"]["table"]
            if reference_table not in selected:
                missing_dependencies.append(f"{entity_name}->{reference_table}")

    assert not missing_dependencies, "Missing selected foreign key dependencies: " + ", ".join(missing_dependencies)
