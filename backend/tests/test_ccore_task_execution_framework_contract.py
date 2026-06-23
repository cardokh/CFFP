import json
from pathlib import Path

from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_STATUS_FAILED,
    CCORE_TASK_EXECUTION_STATUS_SUCCEEDED,
    CCORE_TASK_RUNNER_GENERATE_DOCUMENTATION,
    CCORE_TASK_RUNNER_INSPECT_PROJECT,
    CCORE_TASK_RUNNER_VALIDATE_PROJECT,
)
from backend.src.ccore.tasks.task_execution_runner import (
    CCoreTaskRunnerRegistry,
    GENERATE_DOCUMENTATION_TASK_NAME,
    INSPECT_PROJECT_TASK_NAME,
    VALIDATE_PROJECT_TASK_NAME,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENTITIES_PATH = PROJECT_ROOT / "scripts" / "db" / "postgres" / "config" / "entities.json"
SCHEMA_PATH = PROJECT_ROOT / "scripts" / "db" / "postgres" / "config" / "postgres_create_schema.json"
SEED_PATH = PROJECT_ROOT / "scripts" / "db" / "postgres" / "config" / "postgres_seed_data.json"


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _build_task(task_id: str, task_name: str) -> CCoreTask:
    return CCoreTask(
        task_id=task_id,
        task_name=task_name,
        status_code="PENDING",
    )


def test_task_execution_tables_are_part_of_postgres_schema():
    entities = _load_json(ENTITIES_PATH)
    schema = _load_json(SCHEMA_PATH)

    assert "ccore_task_execution_statuses" in entities["entities"]
    assert "ccore_task_executions" in entities["entities"]
    assert "ccore_task_execution_statuses" in schema["tables"]
    assert "ccore_task_executions" in schema["tables"]


def test_task_execution_statuses_are_seeded():
    seed_data = _load_json(SEED_PATH)
    status_group = next(
        group
        for group in seed_data["seedGroups"]
        if group["table"] == "ccore_task_execution_statuses"
    )
    status_codes = [row["status_code"] for row in status_group["rows"]]

    assert status_group["conflictColumn"] == "status_code"
    assert status_codes == ["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "BLOCKED"]


def test_validate_project_runner_is_registered_as_first_executable_task():
    registry = CCoreTaskRunnerRegistry(project_root=PROJECT_ROOT)
    task = _build_task("22222222-2222-2222-2222-222222222222", VALIDATE_PROJECT_TASK_NAME)

    runner = registry.get_runner_for_task(task)

    assert runner is not None
    assert runner.runner_code == CCORE_TASK_RUNNER_VALIDATE_PROJECT


def test_validate_project_runner_executes_through_automation_factory():
    registry = CCoreTaskRunnerRegistry(project_root=PROJECT_ROOT)
    task = _build_task("22222222-2222-2222-2222-222222222222", VALIDATE_PROJECT_TASK_NAME)

    result = registry.get_runner_for_task(task).execute(task)

    assert result["runner_code"] == CCORE_TASK_RUNNER_VALIDATE_PROJECT
    assert result["status_code"] in {
        CCORE_TASK_EXECUTION_STATUS_SUCCEEDED,
        CCORE_TASK_EXECUTION_STATUS_FAILED,
    }
    assert result["report"]["task"]["name"] == VALIDATE_PROJECT_TASK_NAME
    section_names = [section["name"] for section in result["report"]["sections"]]
    assert section_names == [
        "configuration",
        "python_compilation",
        "javascript_syntax",
        "unit_tests",
    ]
    assert result["report"]["summary"]["sectionCount"] == 4


def test_inspect_project_runner_is_registered_as_second_executable_task():
    registry = CCoreTaskRunnerRegistry(project_root=PROJECT_ROOT)
    task = _build_task("33333333-3333-3333-3333-333333333333", INSPECT_PROJECT_TASK_NAME)

    runner = registry.get_runner_for_task(task)

    assert runner is not None
    assert runner.runner_code == CCORE_TASK_RUNNER_INSPECT_PROJECT


def test_inspect_project_runner_executes_through_automation_factory():
    registry = CCoreTaskRunnerRegistry(project_root=PROJECT_ROOT)
    task = _build_task("33333333-3333-3333-3333-333333333333", INSPECT_PROJECT_TASK_NAME)

    result = registry.get_runner_for_task(task).execute(task)

    assert result["runner_code"] == CCORE_TASK_RUNNER_INSPECT_PROJECT
    assert result["status_code"] in {
        CCORE_TASK_EXECUTION_STATUS_SUCCEEDED,
        CCORE_TASK_EXECUTION_STATUS_FAILED,
    }
    assert result["report"]["task"]["name"] == INSPECT_PROJECT_TASK_NAME
    section_names = [section["name"] for section in result["report"]["sections"]]
    assert section_names == [
        "project_structure",
        "naming_conventions",
        "hardcoded_paths",
        "automation_factory_contracts",
    ]
    assert result["report"]["summary"]["sectionCount"] == 4


def test_generate_documentation_runner_is_registered_as_third_executable_task():
    registry = CCoreTaskRunnerRegistry(project_root=PROJECT_ROOT)
    task = _build_task("44444444-4444-4444-4444-444444444444", GENERATE_DOCUMENTATION_TASK_NAME)

    runner = registry.get_runner_for_task(task)

    assert runner is not None
    assert runner.runner_code == CCORE_TASK_RUNNER_GENERATE_DOCUMENTATION


def test_generate_documentation_runner_executes_through_automation_factory(tmp_path):
    registry = CCoreTaskRunnerRegistry(project_root=PROJECT_ROOT)
    task = _build_task("44444444-4444-4444-4444-444444444444", GENERATE_DOCUMENTATION_TASK_NAME)

    result = registry.get_runner_for_task(task).execute(task)

    assert result["runner_code"] == CCORE_TASK_RUNNER_GENERATE_DOCUMENTATION
    assert result["status_code"] == CCORE_TASK_EXECUTION_STATUS_SUCCEEDED
    assert result["report"]["task"]["name"] == GENERATE_DOCUMENTATION_TASK_NAME
    section_names = [section["name"] for section in result["report"]["sections"]]
    assert section_names == ["documentation_generation"]
    assert result["report"]["summary"]["sectionCount"] == 1

    generated_document = PROJECT_ROOT / "docs" / "automation_factory" / "automation_factory_capabilities.md"
    assert generated_document.is_file()
    generated_text = generated_document.read_text(encoding="utf-8")
    assert "Generate Documentation" in generated_text
    assert "CCore -> Prefect -> Task Runner -> Structured Report -> Execution History" in generated_text
