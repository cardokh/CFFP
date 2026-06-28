"""DB context output contract tests."""

from __future__ import annotations

from automation.factory.crud.db.tests.support.db_json_validation import read_json
from automation.factory.crud.db.tests.support.db_test_paths import get_db_root, get_postgres_root


def test_build_db_context_config_writes_to_own_task_output_folder() -> None:
    db_root = get_db_root()
    config_path = db_root / "postgres" / "build_db_context" / "config" / "build_db_context.json"
    config = read_json(config_path)

    assert config["contextOutputRoot"] == "automation/factory/crud/db/postgres/build_db_context/output"
    context_output_root = db_root.parent.parent.parent.parent / config["contextOutputRoot"]
    expected_output_root = db_root / "postgres" / "build_db_context" / "output"
    assert context_output_root.resolve() == expected_output_root.resolve()


def test_existing_master_context_matches_active_metadata_contract() -> None:
    postgres_root = get_postgres_root()
    metadata_entity_names = read_json(postgres_root / "metadata" / "entities.json")["entities"]
    output_root = postgres_root / "build_db_context" / "output"
    master_context_path = output_root / "master_context.json"

    assert master_context_path.is_file(), "build_db_context output/master_context.json must exist."
    master_context = read_json(master_context_path)

    assert master_context["contextType"] == "database_handoff_context"
    assert master_context["scope"] == "database_only"
    assert master_context["database"]["engine"] == "postgres"
    assert master_context["selectedTables"] == metadata_entity_names
    assert master_context["tableCount"] == len(metadata_entity_names)
    assert master_context["rules"]["containsBackendNaming"] is False
    assert master_context["rules"]["containsFrontendNaming"] is False
    assert master_context["rules"]["downstreamGeneratorsMustApplyTheirOwnBlueprints"] is True

    table_contexts = master_context["tableContexts"]
    assert len(table_contexts) == len(metadata_entity_names)
    assert [entry["tableName"] for entry in table_contexts] == metadata_entity_names

    for entry in table_contexts:
        context_file = entry["contextFile"]
        assert context_file.startswith("automation/factory/crud/db/postgres/build_db_context/output/tables/")
        table_context_path = postgres_root.parents[4] / context_file
        assert table_context_path.is_file(), f"Missing table context file: {context_file}"
        table_context = read_json(table_context_path)
        assert table_context["contextType"] == "database_table_context"
        assert table_context["scope"] == "database_only"
        assert table_context["tableName"] == entry["tableName"]
        assert table_context["sourceFiles"]["schema"].startswith("automation/factory/crud/db/postgres/metadata/entities/")
        assert table_context["sourceFiles"]["seedData"].startswith("automation/factory/crud/db/postgres/metadata/entities/")
        assert isinstance(table_context["columns"], list) and table_context["columns"]
