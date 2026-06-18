"""
Automation task execution service.

Responsibilities:
- Execute one registered automation task through the mandatory CCore blueprint.
- Validate task metadata, configuration, paths, and script governance before execution.
- Run approved task scripts as project-root-relative Python scripts.
- Return structured execution results for manual execution and future pipelines.
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.core.automation.automation_task_execution import (
    AutomationTaskExecutionResult,
)

EXECUTION_STATUS_SUCCESS = "success"
EXECUTION_STATUS_FAILED = "failed"
EXECUTION_STATUS_BLOCKED = "blocked"

EXECUTION_STAGE_VALIDATION = "validation"
EXECUTION_STAGE_EXECUTION = "execution"

VALIDATION_STATUS_PASSED = "PASSED"


class AutomationTaskExecutionService:
    def __init__(
        self,
        project_root,
        automation_task_validation_service,
        timeout_seconds: int = 60,
    ):
        self.project_root = Path(project_root).resolve()
        self.automation_task_validation_service = automation_task_validation_service
        self.timeout_seconds = timeout_seconds

    def execute_task(self, automation_task) -> AutomationTaskExecutionResult:
        execution_id = str(uuid4())
        started_at = self._utc_now()

        validation_report = self.automation_task_validation_service.validate_task(
            automation_task,
        )

        if validation_report.get("status") != VALIDATION_STATUS_PASSED:
            finished_at = self._utc_now()

            return AutomationTaskExecutionResult(
                execution_id=execution_id,
                task_id=automation_task.task_id,
                status=EXECUTION_STATUS_BLOCKED,
                stage=EXECUTION_STAGE_VALIDATION,
                message="Task execution was blocked because validation failed.",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=self._duration_ms(started_at, finished_at),
                return_code=None,
                stdout="",
                stderr="",
                validation=validation_report,
            )

        script_path = self._resolve_project_relative_file_path(
            automation_task.script_path,
        )

        try:
            completed_process = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )

            finished_at = self._utc_now()
            status = (
                EXECUTION_STATUS_SUCCESS
                if completed_process.returncode == 0
                else EXECUTION_STATUS_FAILED
            )

            message = (
                "Task execution completed successfully."
                if status == EXECUTION_STATUS_SUCCESS
                else "Task execution failed."
            )

            return AutomationTaskExecutionResult(
                execution_id=execution_id,
                task_id=automation_task.task_id,
                status=status,
                stage=EXECUTION_STAGE_EXECUTION,
                message=message,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=self._duration_ms(started_at, finished_at),
                return_code=completed_process.returncode,
                stdout=completed_process.stdout,
                stderr=completed_process.stderr,
                validation=validation_report,
            )

        except subprocess.TimeoutExpired as error:
            finished_at = self._utc_now()

            return AutomationTaskExecutionResult(
                execution_id=execution_id,
                task_id=automation_task.task_id,
                status=EXECUTION_STATUS_FAILED,
                stage=EXECUTION_STAGE_EXECUTION,
                message="Task execution timed out.",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=self._duration_ms(started_at, finished_at),
                return_code=None,
                stdout=error.stdout or "",
                stderr=error.stderr or "",
                validation=validation_report,
            )

    def _resolve_project_relative_file_path(self, relative_path: str) -> Path:
        candidate_path = (self.project_root / relative_path).resolve()

        try:
            candidate_path.relative_to(self.project_root)
        except ValueError as error:
            raise ValueError("The script path escapes the project root.") from error

        if not candidate_path.is_file():
            raise FileNotFoundError("The script file does not exist.")

        return candidate_path

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _duration_ms(self, started_at: str, finished_at: str) -> int:
        start = datetime.fromisoformat(started_at)
        finish = datetime.fromisoformat(finished_at)

        return int((finish - start).total_seconds() * 1000)
