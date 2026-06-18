"""
Automation task execution report tests.

Responsibilities:
- Verify that every task execution produces a structured execution report.
- Verify that task-generated JSON artifacts are collected into the report.
- Protect the execution report contract used by the task UI and future pipelines.
"""

from pathlib import Path

from src.core.automation.automation_task import AutomationTask
from src.core.automation.automation_task_execution_service import (
    AutomationTaskExecutionService,
)
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


def test_execute_task_always_returns_persisted_execution_report() -> None:
    project_root = Path(__file__).resolve().parents[2]

    execution_service = AutomationTaskExecutionService(
        project_root=project_root,
        automation_task_validation_service=AutomationTaskValidationService(
            project_root=project_root,
        ),
    )

    result = execution_service.execute_task(
        build_existing_governed_task(),
    )

    execution_report = result.execution_report

    assert execution_report["schema_version"] == "1.0"
    assert execution_report["execution_id"] == result.execution_id
    assert execution_report["task"]["id"] == "inspect-script-governance"
    assert execution_report["summary"]["status"] == result.status
    assert execution_report["summary"]["artifact_count"] >= 1
    assert execution_report["report_path"].startswith("scripts/tasks/output/")
    assert (project_root / execution_report["report_path"]).is_file()


def test_execute_task_collects_task_json_artifacts() -> None:
    project_root = Path(__file__).resolve().parents[2]

    execution_service = AutomationTaskExecutionService(
        project_root=project_root,
        automation_task_validation_service=AutomationTaskValidationService(
            project_root=project_root,
        ),
    )

    result = execution_service.execute_task(
        build_existing_governed_task(),
    )

    artifacts = result.execution_report["artifacts"]

    assert any(
        artifact["name"].startswith("inspect_script_governance_summary_")
        for artifact in artifacts
    )
    assert any(
        artifact.get("summary")
        and "inspectedScriptCount" in artifact["summary"]
        for artifact in artifacts
    )
