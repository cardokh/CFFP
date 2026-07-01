"""Folder boundary tests for the DB-local PostgreSQL implementation layer."""

from __future__ import annotations

from tests.support.db_test_paths import get_postgres_root

VALID_POSTGRES_FOLDERS = {"support", "tasks"}
VALID_POSTGRES_FILES = {"database.json"}
VALID_POSTGRES_TASKS = {"validate_postgres_metadata", "build_database", "insert_data"}
OBSOLETE_POSTGRES_FOLDERS = {"create_table", "add", "context", "metadata", "build_db_context"}


def test_postgres_root_contains_current_implementation_structure() -> None:
    postgres_root = get_postgres_root()
    actual_folders = {path.name for path in postgres_root.iterdir() if path.is_dir()}
    actual_files = {path.name for path in postgres_root.iterdir() if path.is_file()}

    assert actual_folders == VALID_POSTGRES_FOLDERS
    assert VALID_POSTGRES_FILES.issubset(actual_files)
    assert actual_folders.isdisjoint(OBSOLETE_POSTGRES_FOLDERS)


def test_every_postgres_task_has_expected_script_and_config() -> None:
    postgres_root = get_postgres_root()
    tasks_root = postgres_root / "tasks"
    actual_tasks = {path.name for path in tasks_root.iterdir() if path.is_dir()}

    assert actual_tasks == VALID_POSTGRES_TASKS
    for task_name in VALID_POSTGRES_TASKS:
        task_root = tasks_root / task_name
        assert (task_root / f"{task_name}.py").is_file(), f"Missing task script for {task_name}."
        assert (task_root / "config" / f"{task_name}.json").is_file(), f"Missing task config for {task_name}."


def test_task_output_folders_stay_inside_own_task_folder_when_present() -> None:
    postgres_root = get_postgres_root()
    for task_name in VALID_POSTGRES_TASKS:
        output_root = postgres_root / "tasks" / task_name / "output"
        if not output_root.exists():
            continue
        for output_file in output_root.rglob("*"):
            assert output_file.resolve().is_relative_to(output_root.resolve())
