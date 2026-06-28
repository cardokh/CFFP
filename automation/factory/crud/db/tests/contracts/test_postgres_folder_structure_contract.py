"""Folder boundary tests for automation/factory/crud/db/postgres."""

from __future__ import annotations

from automation.factory.crud.db.tests.support.db_test_paths import get_postgres_root

VALID_POSTGRES_FOLDERS = {
    "generate_table_metadata",
    "promote_db_metadata",
    "create_db_schema",
    "seed_db_data",
    "build_db_context",
    "metadata",
}

OBSOLETE_POSTGRES_FOLDERS = {"create_table", "add", "context"}

TASK_FOLDERS = VALID_POSTGRES_FOLDERS - {"metadata"}


def test_postgres_root_contains_only_current_task_folders_and_shared_metadata() -> None:
    postgres_root = get_postgres_root()
    actual_folders = {path.name for path in postgres_root.iterdir() if path.is_dir()}

    assert actual_folders == VALID_POSTGRES_FOLDERS
    assert actual_folders.isdisjoint(OBSOLETE_POSTGRES_FOLDERS)


def test_every_task_folder_has_expected_script_and_config() -> None:
    postgres_root = get_postgres_root()
    for task_name in TASK_FOLDERS:
        task_root = postgres_root / task_name
        assert (task_root / f"{task_name}.py").is_file(), f"Missing task script for {task_name}."
        assert (task_root / "config" / f"{task_name}.json").is_file(), f"Missing task config for {task_name}."


def test_task_output_folders_stay_inside_own_task_folder_when_present() -> None:
    postgres_root = get_postgres_root()
    for task_name in TASK_FOLDERS:
        output_root = postgres_root / task_name / "output"
        if not output_root.exists():
            continue
        for output_file in output_root.rglob("*"):
            assert output_file.resolve().is_relative_to(output_root.resolve())
