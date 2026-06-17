"""
Automation task registry tests.

Responsibilities:
- Verify JSON-based automation task discovery.
- Protect v1 script registry behavior before execution endpoints are added.
"""

import json

from src.core.automation.automation_task_registry import AutomationTaskRegistry


def test_find_all_tasks_returns_registered_tasks(tmp_path) -> None:
    registry_path = tmp_path / "automation_task_registry.json"

    registry_path.write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "id": "inspect-script-governance",
                        "name": "Inspect Script Governance",
                        "description": "Inspects script governance rules.",
                        "category": "validation",
                        "status": "ready",
                        "script_path": "scripts/inspections/governed/inspect_script_governance.py",
                        "config_path": "scripts/inspections/governed/config/inspect_script_governance.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
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
