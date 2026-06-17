"""
Automation task registry tests.

Responsibilities:
- Verify JSON-based automation task discovery.
- Verify inspect-only task configuration loading.
- Protect script registry behavior before execution endpoints are added.
"""

import json

from src.core.automation.automation_task_registry import AutomationTaskRegistry


def write_registry(registry_path, tasks) -> None:
    registry_path.write_text(
        json.dumps(
            {
                "tasks": tasks,
            }
        ),
        encoding="utf-8",
    )


def build_task_entry(task_id="inspect-script-governance") -> dict:
    return {
        "id": task_id,
        "name": "Inspect Script Governance",
        "description": "Inspects script governance rules.",
        "category": "validation",
        "status": "ready",
        "script_path": "scripts/inspections/governed/inspect_script_governance.py",
        "config_path": "scripts/inspections/governed/config/inspect_script_governance.json",
    }


def test_find_all_tasks_returns_registered_tasks(tmp_path) -> None:
    registry_path = tmp_path / "automation_task_registry.json"

    write_registry(
        registry_path=registry_path,
        tasks=[build_task_entry()],
    )

    registry = AutomationTaskRegistry(registry_path=registry_path)

    tasks = registry.find_all_tasks()

    assert len(tasks) == 1
    assert tasks[0].task_id == "inspect-script-governance"
    assert tasks[0].name == "Inspect Script Governance"
    assert tasks[0].category == "validation"
    assert tasks[0].status == "ready"


def test_find_all_tasks_returns_empty_list_when_registry_has_no_tasks(tmp_path) -> None:
    registry_path = tmp_path / "automation_task_registry.json"

    registry_path.write_text(
        json.dumps({}),
        encoding="utf-8",
    )

    registry = AutomationTaskRegistry(registry_path=registry_path)

    assert registry.find_all_tasks() == []


def test_find_task_by_id_returns_matching_task(tmp_path) -> None:
    registry_path = tmp_path / "automation_task_registry.json"

    write_registry(
        registry_path=registry_path,
        tasks=[
            build_task_entry("inspect-script-governance"),
            build_task_entry("validate-registry"),
        ],
    )

    registry = AutomationTaskRegistry(registry_path=registry_path)

    task = registry.find_task_by_id("validate-registry")

    assert task is not None
    assert task.task_id == "validate-registry"


def test_find_task_by_id_returns_none_for_unknown_task(tmp_path) -> None:
    registry_path = tmp_path / "automation_task_registry.json"

    write_registry(
        registry_path=registry_path,
        tasks=[build_task_entry()],
    )

    registry = AutomationTaskRegistry(registry_path=registry_path)

    assert registry.find_task_by_id("missing-task") is None


def test_load_task_configuration_returns_json_data(tmp_path) -> None:
    project_root = tmp_path
    config_path = project_root / "scripts" / "inspections" / "governed" / "config"
    config_path.mkdir(parents=True)
    config_file = config_path / "inspect_script_governance.json"
    config_file.write_text(
        json.dumps(
            {
                "scriptName": "inspect_script_governance",
                "mode": "inspect",
            }
        ),
        encoding="utf-8",
    )

    registry_path = project_root / "automation_task_registry.json"

    write_registry(
        registry_path=registry_path,
        tasks=[build_task_entry()],
    )

    registry = AutomationTaskRegistry(
        registry_path=registry_path,
        project_root=project_root,
    )

    task = registry.find_task_by_id("inspect-script-governance")
    configuration = registry.load_task_configuration(task)

    assert configuration["scriptName"] == "inspect_script_governance"
    assert configuration["mode"] == "inspect"


def test_load_task_configuration_rejects_paths_outside_project_root(tmp_path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    registry_path = project_root / "automation_task_registry.json"
    task_entry = build_task_entry()
    task_entry["config_path"] = "../outside.json"

    write_registry(
        registry_path=registry_path,
        tasks=[task_entry],
    )

    registry = AutomationTaskRegistry(
        registry_path=registry_path,
        project_root=project_root,
    )

    task = registry.find_task_by_id("inspect-script-governance")

    try:
        registry.load_task_configuration(task)
    except ValueError as error:
        assert "inside the project root" in str(error)
    else:
        raise AssertionError("Expected path validation to reject escaped path.")
