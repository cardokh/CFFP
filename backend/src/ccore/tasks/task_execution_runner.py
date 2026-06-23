"""
CCore task execution runners.

Responsibilities:
- Execute registered CCore platform tasks through the Automation Factory layer.
- Use Prefect as the orchestration boundary for task execution.
- Keep concrete task runner logic behind a small runner registry.
- Produce structured reports that can later be consumed by pipelines and UI.
"""

from __future__ import annotations

import compileall
import importlib.util
import json
import os
import re
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
    CCORE_TASK_RUNNER_INSPECT_PROJECT,
    CCORE_TASK_RUNNER_VALIDATE_PROJECT,
)

VALIDATE_PROJECT_TASK_NAME = "Validate Project"
INSPECT_PROJECT_TASK_NAME = "Inspect Project"

STATUS_PASSED = "PASSED"
STATUS_FAILED = "FAILED"
STATUS_SKIPPED = "SKIPPED"

SNAKE_CASE_FILE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.py$")
ABSOLUTE_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:\\\\"),
    re.compile(r"/Users/"),
    re.compile(r"/home/"),
    re.compile(r"/mnt/"),
]


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


@task(name="Inspect CCore Project Structure")
def inspect_project_structure_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    required_paths = [
        "backend/src/ccore/tasks",
        "backend/src/ccore/metrics",
        "backend/src/ccore/application/service_factory.py",
        "backend/tests/test_ccore_task_execution_framework_contract.py",
        "scripts/db/postgres/config/entities.json",
        "scripts/db/postgres/config/postgres_create_schema.json",
        "scripts/db/postgres/config/postgres_seed_data.json",
        "frontend/static/desktop/protected/ccore/js/tasks.js",
        "frontend/static/desktop/protected/ccore/js/task-details.js",
    ]
    checks = []

    for relative_path in required_paths:
        path = root / relative_path
        status = STATUS_PASSED if path.exists() else STATUS_FAILED
        message = "Required CCore path exists." if path.exists() else "Required CCore path is missing."
        checks.append(_build_check(relative_path, status, message))

    return _build_section("project_structure", checks)


@task(name="Inspect CCore Naming Conventions")
def inspect_naming_conventions_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    ccore_source_path = root / "backend" / "src" / "ccore"

    if not ccore_source_path.is_dir():
        return _build_section(
            "naming_conventions",
            [_build_check("backend/src/ccore", STATUS_FAILED, "CCore source directory does not exist.")],
        )

    invalid_files = []
    for python_file in sorted(ccore_source_path.rglob("*.py")):
        if python_file.name == "__init__.py":
            continue
        if not SNAKE_CASE_FILE_NAME_PATTERN.match(python_file.name):
            invalid_files.append(python_file.relative_to(root).as_posix())

    if invalid_files:
        return _build_section(
            "naming_conventions",
            [
                _build_check(
                    "backend/src/ccore/**/*.py",
                    STATUS_FAILED,
                    "Python CCore files must use snake_case names: " + ", ".join(invalid_files[:20]),
                )
            ],
        )

    return _build_section(
        "naming_conventions",
        [_build_check("backend/src/ccore/**/*.py", STATUS_PASSED, "All CCore Python files use snake_case names.")],
    )


@task(name="Inspect CCore Hardcoded Paths")
def inspect_hardcoded_paths_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    scanned_roots = [
        root / "backend" / "src" / "ccore",
        root / "frontend" / "static" / "desktop" / "protected" / "ccore" / "js",
        root / "scripts" / "tests",
    ]
    extensions = {".py", ".js", ".ps1"}
    findings = []

    for scanned_root in scanned_roots:
        if not scanned_root.exists():
            continue
        for file_path in sorted(path for path in scanned_root.rglob("*") if path.is_file() and path.suffix in extensions):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            for pattern in ABSOLUTE_PATH_PATTERNS:
                if pattern.search(text):
                    findings.append(file_path.relative_to(root).as_posix())
                    break

    if findings:
        return _build_section(
            "hardcoded_paths",
            [
                _build_check(
                    "ccore-source-hardcoded-paths",
                    STATUS_FAILED,
                    "Potential hardcoded absolute paths found in: " + ", ".join(findings[:20]),
                )
            ],
        )

    return _build_section(
        "hardcoded_paths",
        [_build_check("ccore-source-hardcoded-paths", STATUS_PASSED, "No hardcoded absolute paths found in scanned CCore files.")],
    )


@task(name="Inspect CCore Automation Factory Contracts")
def inspect_automation_factory_contracts_step(project_root: str) -> dict:
    root = Path(project_root).resolve()
    runner_file = root / "backend" / "src" / "ccore" / "tasks" / "task_execution_runner.py"
    constants_file = root / "backend" / "src" / "ccore" / "tasks" / "task_execution_constants.py"
    checks = []

    if not runner_file.is_file():
        checks.append(_build_check("task_execution_runner.py", STATUS_FAILED, "Task execution runner file is missing."))
    else:
        runner_text = runner_file.read_text(encoding="utf-8")
        checks.append(
            _build_check(
                "ValidateProjectTaskRunner",
                STATUS_PASSED if "ValidateProjectTaskRunner" in runner_text else STATUS_FAILED,
                "Validate Project runner is present." if "ValidateProjectTaskRunner" in runner_text else "Validate Project runner is missing.",
            )
        )
        checks.append(
            _build_check(
                "InspectProjectTaskRunner",
                STATUS_PASSED if "InspectProjectTaskRunner" in runner_text else STATUS_FAILED,
                "Inspect Project runner is present." if "InspectProjectTaskRunner" in runner_text else "Inspect Project runner is missing.",
            )
        )

    if not constants_file.is_file():
        checks.append(_build_check("task_execution_constants.py", STATUS_FAILED, "Task execution constants file is missing."))
    else:
        constants_text = constants_file.read_text(encoding="utf-8")
        checks.append(
            _build_check(
                "CCORE_TASK_RUNNER_INSPECT_PROJECT",
                STATUS_PASSED if "CCORE_TASK_RUNNER_INSPECT_PROJECT" in constants_text else STATUS_FAILED,
                "Inspect Project runner constant is present." if "CCORE_TASK_RUNNER_INSPECT_PROJECT" in constants_text else "Inspect Project runner constant is missing.",
            )
        )

    return _build_section("automation_factory_contracts", checks)


@flow(name="CCore Validate Project")
def validate_project_flow(project_root: str) -> dict:
    configuration_section = validate_project_configuration_step(project_root)
    python_section = compile_ccore_python_step(project_root)
    javascript_section = validate_ccore_javascript_syntax_step(project_root)
    unit_tests_section = run_ccore_unit_tests_step(project_root)
    sections = [configuration_section, python_section, javascript_section, unit_tests_section]
    status = _aggregate_status(sections)

    return _build_report(
        schema_version="1.1",
        task_name=VALIDATE_PROJECT_TASK_NAME,
        runner_code=CCORE_TASK_RUNNER_VALIDATE_PROJECT,
        status=status,
        sections=sections,
    )


@flow(name="CCore Inspect Project")
def inspect_project_flow(project_root: str) -> dict:
    structure_section = inspect_project_structure_step(project_root)
    naming_section = inspect_naming_conventions_step(project_root)
    hardcoded_paths_section = inspect_hardcoded_paths_step(project_root)
    contracts_section = inspect_automation_factory_contracts_step(project_root)
    sections = [structure_section, naming_section, hardcoded_paths_section, contracts_section]
    status = _aggregate_status(sections)

    return _build_report(
        schema_version="1.0",
        task_name=INSPECT_PROJECT_TASK_NAME,
        runner_code=CCORE_TASK_RUNNER_INSPECT_PROJECT,
        status=status,
        sections=sections,
    )


class ValidateProjectTaskRunner:
    runner_code = CCORE_TASK_RUNNER_VALIDATE_PROJECT

    def __init__(self, project_root):
        self.project_root = Path(project_root).resolve()

    def execute(self, task: CCoreTask) -> dict:
        report = validate_project_flow(str(self.project_root))
        return _build_runner_result(self.runner_code, report)


class InspectProjectTaskRunner:
    runner_code = CCORE_TASK_RUNNER_INSPECT_PROJECT

    def __init__(self, project_root):
        self.project_root = Path(project_root).resolve()

    def execute(self, task: CCoreTask) -> dict:
        report = inspect_project_flow(str(self.project_root))
        return _build_runner_result(self.runner_code, report)


class CCoreTaskRunnerRegistry:
    def __init__(self, project_root):
        self.project_root = Path(project_root).resolve()
        self.runners_by_task_name = {
            VALIDATE_PROJECT_TASK_NAME: ValidateProjectTaskRunner(self.project_root),
            INSPECT_PROJECT_TASK_NAME: InspectProjectTaskRunner(self.project_root),
        }

    def get_runner_for_task(self, task: CCoreTask) -> CCoreTaskRunnerProtocol | None:
        return self.runners_by_task_name.get(task.task_name)


def _build_runner_result(runner_code: str, report: dict) -> dict:
    return {
        "status_code": (
            CCORE_TASK_EXECUTION_STATUS_SUCCEEDED
            if report.get("status") == STATUS_PASSED
            else CCORE_TASK_EXECUTION_STATUS_FAILED
        ),
        "runner_code": runner_code,
        "report": report,
    }


def _build_report(schema_version: str, task_name: str, runner_code: str, status: str, sections: list[dict]) -> dict:
    return {
        "schemaVersion": schema_version,
        "task": {
            "name": task_name,
            "runnerCode": runner_code,
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
