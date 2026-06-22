"""
CCore task execution runners.

Responsibilities:
- Execute registered CCore platform tasks through the Automation Factory layer.
- Use Prefect as the orchestration boundary for task execution.
- Keep concrete task runner logic behind a small runner registry.
"""

from __future__ import annotations

import compileall
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from src.infrastructure.orchestration.prefect.prefect_compat import flow, task
from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_STATUS_FAILED,
    CCORE_TASK_EXECUTION_STATUS_SUCCEEDED,
    CCORE_TASK_RUNNER_VALIDATE_PROJECT,
)

VALIDATE_PROJECT_TASK_NAME = "Validate Project"


class CCoreTaskRunnerProtocol(Protocol):
    runner_code: str

    def execute(self, task: CCoreTask) -> dict:
        """Execute one CCore task and return a report."""


@task(name="Validate CCore Project Configuration")
def validate_project_configuration_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    config_paths = [
        root / "backend" / "src" / "ccore" / "shared" / "config" / "app_config.json",
        root / "backend" / "src" / "ccore" / "shared" / "config" / "app_path_utils.json",
        root / "scripts" / "db" / "postgres" / "config" / "postgres_create_schema.json",
        root / "scripts" / "db" / "postgres" / "config" / "postgres_seed_data.json",
    ]
    checks = []

    for config_path in config_paths:
        relative_path = config_path.relative_to(root).as_posix()
        if not config_path.is_file():
            checks.append(_build_check(relative_path, "FAILED", "Configuration file is missing."))
            continue

        try:
            json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            checks.append(
                _build_check(
                    relative_path,
                    "FAILED",
                    f"Configuration JSON is invalid: {error.msg}.",
                )
            )
            continue

        checks.append(_build_check(relative_path, "PASSED", "Configuration file exists and is valid JSON."))

    return {
        "name": "configuration",
        "status": _aggregate_status(checks),
        "checks": checks,
    }


@task(name="Compile CCore Python")
def compile_ccore_python_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    ccore_source_path = root / "backend" / "src" / "ccore"

    if not ccore_source_path.is_dir():
        return {
            "name": "python_compilation",
            "status": "FAILED",
            "checks": [
                _build_check(
                    "backend/src/ccore",
                    "FAILED",
                    "CCore source directory does not exist.",
                )
            ],
        }

    passed = compileall.compile_dir(
        str(ccore_source_path),
        quiet=1,
        force=True,
    )

    status = "PASSED" if passed else "FAILED"
    return {
        "name": "python_compilation",
        "status": status,
        "checks": [
            _build_check(
                "backend/src/ccore",
                status,
                "CCore Python compilation completed." if passed else "CCore Python compilation failed.",
            )
        ],
    }


@flow(name="CCore Validate Project")
def validate_project_flow(project_root: str) -> dict:
    configuration_section = validate_project_configuration_step(project_root)
    python_section = compile_ccore_python_step(project_root)
    sections = [configuration_section, python_section]
    status = _aggregate_status(sections)

    return {
        "schemaVersion": "1.0",
        "task": {
            "name": VALIDATE_PROJECT_TASK_NAME,
            "runnerCode": CCORE_TASK_RUNNER_VALIDATE_PROJECT,
        },
        "status": status,
        "sections": sections,
        "summary": {
            "sectionCount": len(sections),
            "passedSectionCount": len([section for section in sections if section["status"] == "PASSED"]),
            "failedSectionCount": len([section for section in sections if section["status"] != "PASSED"]),
        },
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


class ValidateProjectTaskRunner:
    runner_code = CCORE_TASK_RUNNER_VALIDATE_PROJECT

    def __init__(self, project_root):
        self.project_root = Path(project_root).resolve()

    def execute(self, task: CCoreTask) -> dict:
        report = validate_project_flow(str(self.project_root))
        return {
            "status_code": (
                CCORE_TASK_EXECUTION_STATUS_SUCCEEDED
                if report.get("status") == "PASSED"
                else CCORE_TASK_EXECUTION_STATUS_FAILED
            ),
            "runner_code": self.runner_code,
            "report": report,
        }


class CCoreTaskRunnerRegistry:
    def __init__(self, project_root):
        self.project_root = Path(project_root).resolve()
        self.runners_by_task_name = {
            VALIDATE_PROJECT_TASK_NAME: ValidateProjectTaskRunner(self.project_root),
        }

    def get_runner_for_task(self, task: CCoreTask) -> CCoreTaskRunnerProtocol | None:
        return self.runners_by_task_name.get(task.task_name)


def _build_check(check_id: str, status: str, message: str) -> dict:
    return {
        "id": check_id,
        "status": status,
        "message": message,
    }


def _aggregate_status(items: list[dict]) -> str:
    return "PASSED" if all(item.get("status") == "PASSED" for item in items) else "FAILED"
