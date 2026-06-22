"""
CCore task execution runners.

Responsibilities:
- Execute registered CCore platform tasks through the Automation Factory layer.
- Use Prefect as the orchestration boundary for task execution.
- Keep concrete task runner logic behind a small runner registry.
- Produce structured validation reports that can later be consumed by pipelines and UI.
"""

from __future__ import annotations

import compileall
import importlib.util
import json
import os
import shutil
import subprocess
import sys
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

STATUS_PASSED = "PASSED"
STATUS_FAILED = "FAILED"
STATUS_SKIPPED = "SKIPPED"


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
            checks.append(_build_check(relative_path, STATUS_FAILED, "Configuration file is missing."))
            continue

        try:
            json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            checks.append(
                _build_check(
                    relative_path,
                    STATUS_FAILED,
                    f"Configuration JSON is invalid: {error.msg}.",
                )
            )
            continue

        checks.append(_build_check(relative_path, STATUS_PASSED, "Configuration file exists and is valid JSON."))

    return _build_section("configuration", checks)


@task(name="Compile CCore Python")
def compile_ccore_python_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    ccore_source_path = root / "backend" / "src" / "ccore"

    if not ccore_source_path.is_dir():
        return _build_section(
            "python_compilation",
            [
                _build_check(
                    "backend/src/ccore",
                    STATUS_FAILED,
                    "CCore source directory does not exist.",
                )
            ],
        )

    passed = compileall.compile_dir(
        str(ccore_source_path),
        quiet=1,
        force=True,
    )

    status = STATUS_PASSED if passed else STATUS_FAILED
    return _build_section(
        "python_compilation",
        [
            _build_check(
                "backend/src/ccore",
                status,
                "CCore Python compilation completed." if passed else "CCore Python compilation failed.",
            )
        ],
    )


@task(name="Validate CCore JavaScript Syntax")
def validate_ccore_javascript_syntax_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    ccore_js_path = root / "frontend" / "static" / "desktop" / "protected" / "ccore" / "js"

    if not ccore_js_path.is_dir():
        return _build_section(
            "javascript_syntax",
            [
                _build_check(
                    "frontend/static/desktop/protected/ccore/js",
                    STATUS_SKIPPED,
                    "CCore JavaScript directory does not exist.",
                )
            ],
        )

    node_path = shutil.which("node")
    if node_path is None:
        return _build_section(
            "javascript_syntax",
            [
                _build_check(
                    "node",
                    STATUS_SKIPPED,
                    "Node.js was not found, so JavaScript syntax validation was skipped.",
                )
            ],
        )

    checks = []
    javascript_files = sorted(ccore_js_path.glob("*.js"))

    if not javascript_files:
        return _build_section(
            "javascript_syntax",
            [
                _build_check(
                    "frontend/static/desktop/protected/ccore/js",
                    STATUS_SKIPPED,
                    "No CCore JavaScript files were found.",
                )
            ],
        )

    for javascript_file in javascript_files:
        relative_path = javascript_file.relative_to(root).as_posix()
        result = subprocess.run(
            [node_path, "--check", str(javascript_file)],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
        status = STATUS_PASSED if result.returncode == 0 else STATUS_FAILED
        message = "JavaScript syntax check passed."
        if result.returncode != 0:
            message = _trim_process_output(result.stderr or result.stdout or "JavaScript syntax check failed.")
        checks.append(_build_check(relative_path, status, message))

    return _build_section("javascript_syntax", checks)


@task(name="Run CCore Unit Tests")
def run_ccore_unit_tests_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    test_paths = [
        root / "backend" / "tests" / "test_ccore_automation_factory_seed_data.py",
        root / "backend" / "tests" / "test_ccore_metrics_blueprint_contract.py",
        root / "backend" / "tests" / "test_ccore_tasks_golden_contract.py",
        root / "backend" / "tests" / "test_ccore_task_execution_framework_contract.py",
    ]
    existing_test_paths = [test_path for test_path in test_paths if test_path.is_file()]

    if not existing_test_paths:
        return _build_section(
            "unit_tests",
            [
                _build_check(
                    "backend/tests/test_ccore_*.py",
                    STATUS_SKIPPED,
                    "No CCore contract tests were found.",
                )
            ],
        )

    if importlib.util.find_spec("pytest") is None:
        return _build_section(
            "unit_tests",
            [
                _build_check(
                    "pytest",
                    STATUS_SKIPPED,
                    "pytest is not installed in the active Python environment, so unit tests were skipped.",
                )
            ],
        )

    if os.environ.get("CCORE_VALIDATE_RUN_UNIT_TESTS") != "1":
        return _build_section(
            "unit_tests",
            [
                _build_check(
                    "backend/tests/test_ccore_*.py",
                    STATUS_SKIPPED,
                    "Unit test execution is available but disabled by default. Set CCORE_VALIDATE_RUN_UNIT_TESTS=1 to enable it.",
                )
            ],
        )

    command = [
        sys.executable,
        "-m",
        "pytest",
        *[test_path.relative_to(root).as_posix() for test_path in existing_test_paths],
        "-q",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return _build_section(
            "unit_tests",
            [
                _build_check(
                    "backend/tests/test_ccore_*.py",
                    STATUS_FAILED,
                    "CCore unit tests exceeded the 30 second validation timeout.",
                )
            ],
        )

    status = STATUS_PASSED if result.returncode == 0 else STATUS_FAILED
    message = "CCore unit tests passed." if result.returncode == 0 else _trim_process_output(result.stdout + result.stderr)

    return _build_section(
        "unit_tests",
        [
            _build_check(
                "backend/tests/test_ccore_*.py",
                status,
                message,
            )
        ],
    )


@flow(name="CCore Validate Project")
def validate_project_flow(project_root: str) -> dict:
    configuration_section = validate_project_configuration_step(project_root)
    python_section = compile_ccore_python_step(project_root)
    javascript_section = validate_ccore_javascript_syntax_step(project_root)
    unit_tests_section = run_ccore_unit_tests_step(project_root)
    sections = [configuration_section, python_section, javascript_section, unit_tests_section]
    status = _aggregate_status(sections)

    return {
        "schemaVersion": "1.1",
        "task": {
            "name": VALIDATE_PROJECT_TASK_NAME,
            "runnerCode": CCORE_TASK_RUNNER_VALIDATE_PROJECT,
        },
        "status": status,
        "sections": sections,
        "summary": {
            "sectionCount": len(sections),
            "passedSectionCount": len([section for section in sections if section["status"] == STATUS_PASSED]),
            "failedSectionCount": len([section for section in sections if section["status"] == STATUS_FAILED]),
            "skippedSectionCount": len([section for section in sections if section["status"] == STATUS_SKIPPED]),
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
                if report.get("status") == STATUS_PASSED
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


def _build_section(name: str, checks: list[dict]) -> dict:
    return {
        "name": name,
        "status": _aggregate_status(checks),
        "checks": checks,
    }


def _aggregate_status(items: list[dict]) -> str:
    if any(item.get("status") == STATUS_FAILED for item in items):
        return STATUS_FAILED

    if items and all(item.get("status") == STATUS_SKIPPED for item in items):
        return STATUS_SKIPPED

    return STATUS_PASSED


def _trim_process_output(output: str, limit: int = 2000) -> str:
    normalized_output = " ".join(output.split())
    if len(normalized_output) <= limit:
        return normalized_output

    return f"{normalized_output[:limit]}..."
