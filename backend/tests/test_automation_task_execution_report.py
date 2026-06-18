"""
Automation task execution report tests.

Responsibilities:
- Verify that every task execution produces a structured execution report.
- Verify that task-generated JSON artifacts are collected into the report.
- Verify that task, configuration, validation, and log snapshots are captured per execution.
- Protect the execution report contract used by the task UI and future pipelines.
"""

import json
import subprocess
from pathlib import Path

from src.core.automation.automation_task import AutomationTask
from src.core.automation.automation_task_execution_service import (
    AutomationTaskExecutionService,
)


class PassingValidationService:
    def validate_task(self, automation_task):
        return {
            "status": "PASSED",
            "summary": {
                "check_count": 1,
                "passed_check_count": 1,
                "failed_check_count": 0,
            },
            "checks": [
                {
                    "status": "PASSED",
                    "label": "Test validation",
                    "message": "Validation passed for test task.",
                }
            ],
        }


class FailingValidationService:
    def validate_task(self, automation_task):
        return {
            "status": "FAILED",
            "summary": {
                "check_count": 1,
                "passed_check_count": 0,
                "failed_check_count": 1,
            },
            "checks": [
                {
                    "status": "FAILED",
                    "label": "Test validation",
                    "message": "Validation failed for test task.",
                }
            ],
        }


def build_test_task(project_root: Path) -> AutomationTask:
    script_path = project_root / "scripts" / "tasks" / "test_task.py"
    config_path = project_root / "scripts" / "tasks" / "config" / "test_task.json"
    output_path = project_root / "scripts" / "tasks" / "output"

    script_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    script_path.write_text(
        "print('PASS test task')\n",
        encoding="utf-8",
    )

    config_path.write_text(
        json.dumps(
            {
                "scriptName": "test_task",
                "mode": "test",
            }
        ),
        encoding="utf-8",
    )

    return AutomationTask(
        task_id="test-task",
        name="Test Task",
        description="Test execution task.",
        category="validation",
        status="ready",
        script_path="scripts/tasks/test_task.py",
        config_path="scripts/tasks/config/test_task.json",
    )


def build_execution_service(project_root: Path, validation_service):
    return AutomationTaskExecutionService(
        project_root=project_root,
        automation_task_validation_service=validation_service,
        timeout_seconds=10,
    )


def install_fake_subprocess_run(monkeypatch, project_root: Path):
    def fake_run(*args, **kwargs):
        output_directory = project_root / "scripts" / "tasks" / "output"
        output_directory.mkdir(parents=True, exist_ok=True)
        (output_directory / "test_task_artifact.json").write_text(
            json.dumps(
                {
                    "summary": {
                        "inspectedScriptCount": 1,
                        "passedScriptCount": 1,
                        "failedScriptCount": 0,
                        "findingCount": 1,
                    },
                    "inspectedFiles": [
                        {
                            "filePath": "scripts/tasks/test_task.py",
                            "status": "PASSED",
                            "findingCount": 1,
                            "failedFindingCount": 0,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="PASS test task\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)


def execute_test_task(tmp_path, monkeypatch, validation_service=None):
    automation_task = build_test_task(tmp_path)
    install_fake_subprocess_run(monkeypatch, tmp_path)
    execution_service = build_execution_service(
        tmp_path,
        validation_service or PassingValidationService(),
    )

    return execution_service.execute_task(
        automation_task,
    ), execution_service


def test_execute_task_always_returns_persisted_execution_report(tmp_path, monkeypatch) -> None:
    result, _ = execute_test_task(tmp_path, monkeypatch)

    execution_report = result.execution_report

    assert execution_report["schema_version"] == "1.1"
    assert execution_report["execution_id"] == result.execution_id
    assert execution_report["task"]["id"] == "test-task"
    assert execution_report["summary"]["status"] == result.status
    assert execution_report["summary"]["artifact_count"] == 1
    assert execution_report["report_path"].startswith("scripts/tasks/output/")
    assert (tmp_path / execution_report["report_path"]).is_file()


def test_execute_task_collects_task_json_artifacts(tmp_path, monkeypatch) -> None:
    result, _ = execute_test_task(tmp_path, monkeypatch)

    artifacts = result.execution_report["artifacts"]

    assert any(
        artifact["name"] == "test_task_artifact.json"
        for artifact in artifacts
    )
    assert any(
        artifact.get("summary")
        and "inspectedScriptCount" in artifact["summary"]
        for artifact in artifacts
    )


def test_execute_task_report_contains_task_configuration_validation_and_logs_snapshots(tmp_path, monkeypatch) -> None:
    result, _ = execute_test_task(tmp_path, monkeypatch)

    execution_report = result.execution_report

    assert execution_report["schema_version"] == "1.1"
    assert execution_report["task"]["id"] == "test-task"
    assert execution_report["configuration"]["path"] == "scripts/tasks/config/test_task.json"
    assert execution_report["configuration"]["content"]["scriptName"] == "test_task"
    assert execution_report["validation"]["status"] == "PASSED"
    assert execution_report["logs"]["stdout"] == result.stdout
    assert execution_report["logs"]["stderr"] == result.stderr


def test_blocked_task_execution_still_captures_configuration_and_validation_snapshots(tmp_path, monkeypatch) -> None:
    result, _ = execute_test_task(
        tmp_path,
        monkeypatch,
        FailingValidationService(),
    )

    execution_report = result.execution_report

    assert result.status == "blocked"
    assert execution_report["summary"]["stage"] == "validation"
    assert execution_report["configuration"]["content"]["scriptName"] == "test_task"
    assert execution_report["validation"]["status"] == "FAILED"
    assert execution_report["logs"]["stdout"] == ""
    assert execution_report["logs"]["stderr"] == ""


def test_list_and_read_task_execution_reports_by_execution_id(tmp_path, monkeypatch) -> None:
    result, execution_service = execute_test_task(tmp_path, monkeypatch)

    execution_summaries = execution_service.list_task_execution_reports(
        "test-task"
    )

    assert any(
        execution_summary["execution_id"] == result.execution_id
        for execution_summary in execution_summaries
    )

    execution_report = execution_service.get_task_execution_report(
        "test-task",
        result.execution_id,
    )

    assert execution_report is not None
    assert execution_report["execution_id"] == result.execution_id
    assert execution_report["configuration"]["path"] == "scripts/tasks/config/test_task.json"
