"""
Automation task validation tests.

Responsibilities:
- Verify pre-execution validation report behavior.
- Protect file path, configuration JSON, and script governance validation.
"""

from pathlib import Path

from src.core.automation.automation_task import AutomationTask
from src.core.automation.automation_task_validation import (
    AutomationTaskValidationService,
)


def build_existing_governed_task() -> AutomationTask:
    return AutomationTask(
        task_id="inspect-script-governance",
        name="Inspect Script Governance",
        description="Inspects registered scripts against CFFP scripting governance rules.",
        category="validation",
        status="ready",
        script_path="scripts/inspections/governed/inspect_script_governance.py",
        config_path="scripts/inspections/governed/config/inspect_script_governance.json",
    )


def test_validate_task_reports_passed_for_existing_governed_script() -> None:
    project_root = Path(__file__).resolve().parents[2]

    validation_service = AutomationTaskValidationService(
        project_root=project_root,
    )

    report = validation_service.validate_task(
        build_existing_governed_task(),
    )

    assert report["status"] == "PASSED"
    assert report["summary"]["failed_check_count"] == 0
    assert any(
        check["id"] == "script-governance" and check["status"] == "PASSED"
        for check in report["checks"]
    )


def test_validate_task_reports_failed_for_missing_script(tmp_path) -> None:
    config_path = tmp_path / "config" / "task.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "{}",
        encoding="utf-8",
    )

    automation_task = AutomationTask(
        task_id="missing-script",
        name="Missing Script",
        description="Missing script test task.",
        category="validation",
        status="draft",
        script_path="scripts/missing.py",
        config_path="config/task.json",
    )

    validation_service = AutomationTaskValidationService(
        project_root=tmp_path,
    )

    report = validation_service.validate_task(
        automation_task,
    )

    assert report["status"] == "FAILED"
    assert any(
        check["id"] == "script-path" and check["status"] == "FAILED"
        for check in report["checks"]
    )
