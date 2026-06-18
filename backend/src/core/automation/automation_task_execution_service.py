"""
Automation task execution service.

Responsibilities:
- Execute one registered automation task through the mandatory CCore blueprint.
- Validate task metadata, configuration, paths, and script governance before execution.
- Run approved task scripts as project-root-relative Python scripts.
- Always produce a structured execution report for every task execution attempt.
- Capture task definition, configuration, and validation snapshots per execution.
- Collect task-generated JSON artifacts and expose them through the report contract.
- List and read persisted task execution reports for execution-history views.
- Return structured execution results for manual execution and future pipelines.
"""

import json
import os
import re
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

EXECUTION_STAGE_CONFIGURATION = "configuration"
EXECUTION_STAGE_VALIDATION = "validation"
EXECUTION_STAGE_GOVERNANCE = "governance"
EXECUTION_STAGE_EXECUTION = "execution"
EXECUTION_STAGE_ARTIFACT_COLLECTION = "artifact_collection"
EXECUTION_STAGE_REPORTING = "reporting"

VALIDATION_STATUS_PASSED = "PASSED"
VALIDATION_STATUS_UNKNOWN = "UNKNOWN"

DEFAULT_EXECUTION_REPORT_SCHEMA_VERSION = "1.2"
DEFAULT_TASK_ARTIFACT_OUTPUT_DIRECTORY_NAME = "output"
DEFAULT_TIMEOUT_SECONDS = 60

CONFIGURATION_SNAPSHOT_STATUS_AVAILABLE = "available"
CONFIGURATION_SNAPSHOT_STATUS_FAILED = "failed"

ARTIFACT_STATUS_AVAILABLE = "available"
ARTIFACT_STATUS_FAILED = "failed"

JSON_FILE_PATTERN = "*.json"
EXECUTION_REPORT_FILE_TEMPLATE = "{task_id}_execution_{timestamp}.json"


class AutomationTaskExecutionService:
    def __init__(
        self,
        project_root,
        automation_task_validation_service,
        execution_report_output_directory=None,
        task_artifact_output_directory_name: str = DEFAULT_TASK_ARTIFACT_OUTPUT_DIRECTORY_NAME,
        execution_report_schema_version: str = DEFAULT_EXECUTION_REPORT_SCHEMA_VERSION,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.project_root = Path(project_root).resolve()
        self.automation_task_validation_service = automation_task_validation_service
        self.timeout_seconds = timeout_seconds
        self.execution_report_schema_version = execution_report_schema_version
        self.task_artifact_output_directory_name = task_artifact_output_directory_name
        self.execution_report_output_directory = self._resolve_output_directory(
            execution_report_output_directory,
        )

    def execute_task(self, automation_task) -> AutomationTaskExecutionResult:
        execution_id = str(uuid4())
        started_at = self._utc_now()
        execution_started_at = datetime.fromisoformat(started_at)
        task_snapshot = self._build_task_snapshot(automation_task)
        configuration_snapshot = self._load_configuration_snapshot(automation_task)
        validation_report = self._validate_task_safely(automation_task)

        if validation_report.get("status") != VALIDATION_STATUS_PASSED:
            return self._finish_execution(
                automation_task=automation_task,
                task_snapshot=task_snapshot,
                configuration_snapshot=configuration_snapshot,
                execution_id=execution_id,
                status=EXECUTION_STATUS_BLOCKED,
                stage=EXECUTION_STAGE_VALIDATION,
                message="Task execution was blocked because validation failed.",
                started_at=started_at,
                return_code=None,
                stdout="",
                stderr="",
                validation_report=validation_report,
                artifacts=[],
            )

        try:
            script_path = self._resolve_project_relative_file_path(
                automation_task.script_path,
            )
        except (FileNotFoundError, ValueError) as error:
            return self._finish_execution(
                automation_task=automation_task,
                task_snapshot=task_snapshot,
                configuration_snapshot=configuration_snapshot,
                execution_id=execution_id,
                status=EXECUTION_STATUS_BLOCKED,
                stage=EXECUTION_STAGE_VALIDATION,
                message=str(error),
                started_at=started_at,
                return_code=None,
                stdout="",
                stderr="",
                validation_report=validation_report,
                artifacts=[],
            )

        try:
            completed_process = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                env=self._build_subprocess_environment(),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )

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

            artifacts = self._collect_json_artifacts(
                script_path=script_path,
                configuration_snapshot=configuration_snapshot,
                execution_started_at=execution_started_at,
            )

            return self._finish_execution(
                automation_task=automation_task,
                task_snapshot=task_snapshot,
                configuration_snapshot=configuration_snapshot,
                execution_id=execution_id,
                status=status,
                stage=EXECUTION_STAGE_EXECUTION,
                message=message,
                started_at=started_at,
                return_code=completed_process.returncode,
                stdout=completed_process.stdout,
                stderr=completed_process.stderr,
                validation_report=validation_report,
                artifacts=artifacts,
            )

        except subprocess.TimeoutExpired as error:
            return self._finish_execution(
                automation_task=automation_task,
                task_snapshot=task_snapshot,
                configuration_snapshot=configuration_snapshot,
                execution_id=execution_id,
                status=EXECUTION_STATUS_FAILED,
                stage=EXECUTION_STAGE_EXECUTION,
                message="Task execution timed out.",
                started_at=started_at,
                return_code=None,
                stdout=error.stdout or "",
                stderr=error.stderr or "",
                validation_report=validation_report,
                artifacts=[],
            )

        except OSError as error:
            return self._finish_execution(
                automation_task=automation_task,
                task_snapshot=task_snapshot,
                configuration_snapshot=configuration_snapshot,
                execution_id=execution_id,
                status=EXECUTION_STATUS_FAILED,
                stage=EXECUTION_STAGE_EXECUTION,
                message="Task execution failed before the script completed.",
                started_at=started_at,
                return_code=None,
                stdout="",
                stderr=str(error),
                validation_report=validation_report,
                artifacts=[],
            )

    def list_task_execution_reports(self, task_id: str) -> list[dict]:
        normalized_task_id = str(task_id or "").strip()

        if not normalized_task_id or not self.execution_report_output_directory.is_dir():
            return []

        execution_summaries = []

        for report_path in sorted(
            self.execution_report_output_directory.glob(
                EXECUTION_REPORT_FILE_TEMPLATE.format(
                    task_id=self._safe_file_component(normalized_task_id),
                    timestamp="*",
                )
            ),
            reverse=True,
        ):
            execution_report = self._read_execution_report_path(report_path)

            if not execution_report:
                continue

            if execution_report.get("task", {}).get("id") != normalized_task_id:
                continue

            execution_summaries.append(
                self._execution_report_to_summary(execution_report)
            )

        return execution_summaries

    def get_task_execution_report(
        self,
        task_id: str,
        execution_id: str,
    ) -> dict | None:
        normalized_task_id = str(task_id or "").strip()
        normalized_execution_id = str(execution_id or "").strip()

        if not normalized_task_id or not normalized_execution_id:
            return None

        for report_path in sorted(
            self.execution_report_output_directory.glob(
                EXECUTION_REPORT_FILE_TEMPLATE.format(
                    task_id=self._safe_file_component(normalized_task_id),
                    timestamp="*",
                )
            ),
            reverse=True,
        ):
            execution_report = self._read_execution_report_path(report_path)

            if not execution_report:
                continue

            if execution_report.get("task", {}).get("id") != normalized_task_id:
                continue

            if execution_report.get("execution_id") == normalized_execution_id:
                return execution_report

        return None

    def _finish_execution(
        self,
        automation_task,
        task_snapshot: dict,
        configuration_snapshot: dict,
        execution_id: str,
        status: str,
        stage: str,
        message: str,
        started_at: str,
        return_code: int | None,
        stdout: str,
        stderr: str,
        validation_report: dict,
        artifacts: list[dict],
    ) -> AutomationTaskExecutionResult:
        finished_at = self._utc_now()
        duration_ms = self._duration_ms(started_at, finished_at)
        execution_report = self._build_execution_report(
            task_snapshot=task_snapshot,
            configuration_snapshot=configuration_snapshot,
            execution_id=execution_id,
            status=status,
            stage=stage,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            validation_report=validation_report,
            artifacts=artifacts,
        )
        execution_report = self._persist_execution_report(execution_report)

        return AutomationTaskExecutionResult(
            execution_id=execution_id,
            task_id=automation_task.task_id,
            status=status,
            stage=stage,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            validation=validation_report,
            execution_report=execution_report,
        )

    def _validate_task_safely(self, automation_task) -> dict:
        try:
            return self.automation_task_validation_service.validate_task(
                automation_task,
            )
        except Exception as error:
            return {
                "task_id": automation_task.task_id,
                "status": "FAILED",
                "summary": {
                    "check_count": 1,
                    "passed_check_count": 0,
                    "failed_check_count": 1,
                },
                "checks": [
                    {
                        "id": "validation-service",
                        "label": "Validation service",
                        "status": "FAILED",
                        "message": "Task validation failed to complete.",
                        "details": {
                            "error": str(error),
                        },
                    }
                ],
            }

    def _build_task_snapshot(self, automation_task) -> dict:
        return {
            "id": automation_task.task_id,
            "name": automation_task.name,
            "description": automation_task.description,
            "category": automation_task.category,
            "status": automation_task.status,
            "script_path": automation_task.script_path,
            "config_path": automation_task.config_path,
        }

    def _load_configuration_snapshot(self, automation_task) -> dict:
        snapshot = {
            "path": automation_task.config_path,
            "status": CONFIGURATION_SNAPSHOT_STATUS_FAILED,
            "content": None,
        }

        try:
            config_path = self._resolve_project_relative_file_path(
                automation_task.config_path,
            )
            snapshot["content"] = json.loads(
                config_path.read_text(
                    encoding="utf-8",
                )
            )
            snapshot["status"] = CONFIGURATION_SNAPSHOT_STATUS_AVAILABLE
        except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as error:
            snapshot["error"] = str(error)

        return snapshot

    def _build_subprocess_environment(self) -> dict:
        environment = dict(os.environ)
        existing_python_path = environment.get("PYTHONPATH", "")
        project_root_path = str(self.project_root)

        if existing_python_path:
            environment["PYTHONPATH"] = f"{project_root_path}{os.pathsep}{existing_python_path}"
        else:
            environment["PYTHONPATH"] = project_root_path

        return environment

    def _build_execution_report(
        self,
        task_snapshot: dict,
        configuration_snapshot: dict,
        execution_id: str,
        status: str,
        stage: str,
        message: str,
        started_at: str,
        finished_at: str,
        duration_ms: int,
        return_code: int | None,
        stdout: str,
        stderr: str,
        validation_report: dict,
        artifacts: list[dict],
    ) -> dict:
        failed_artifacts = [
            artifact
            for artifact in artifacts
            if artifact.get("status") == ARTIFACT_STATUS_FAILED
        ]

        return {
            "schema_version": self.execution_report_schema_version,
            "execution_id": execution_id,
            "task": task_snapshot,
            "configuration": configuration_snapshot,
            "summary": {
                "status": status,
                "stage": stage,
                "message": message,
                "return_code": return_code,
                "started_at": started_at,
                "finished_at": finished_at,
                "duration_ms": duration_ms,
                "validation_status": validation_report.get(
                    "status",
                    VALIDATION_STATUS_UNKNOWN,
                ),
                "configuration_status": configuration_snapshot.get(
                    "status",
                    CONFIGURATION_SNAPSHOT_STATUS_FAILED,
                ),
                "artifact_count": len(artifacts),
                "failed_artifact_count": len(failed_artifacts),
            },
            "validation": validation_report,
            "logs": {
                "stdout": stdout,
                "stderr": stderr,
            },
            "artifacts": artifacts,
        }

    def _persist_execution_report(self, execution_report: dict) -> dict:
        self.execution_report_output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        task_id = self._safe_file_component(
            execution_report["task"]["id"],
        )
        timestamp = self._safe_timestamp(
            execution_report["summary"]["started_at"],
        )
        report_path = (
            self.execution_report_output_directory
            / EXECUTION_REPORT_FILE_TEMPLATE.format(
                task_id=task_id,
                timestamp=timestamp,
            )
        )

        execution_report["report_path"] = self._to_project_relative_path(
            report_path,
        )

        report_path.write_text(
            json.dumps(
                execution_report,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return execution_report

    def _read_execution_report_path(self, report_path: Path) -> dict | None:
        try:
            return json.loads(
                report_path.read_text(
                    encoding="utf-8",
                )
            )
        except (OSError, json.JSONDecodeError):
            return None

    def _execution_report_to_summary(self, execution_report: dict) -> dict:
        summary = execution_report.get("summary", {})

        return {
            "execution_id": execution_report.get("execution_id", ""),
            "task_id": execution_report.get("task", {}).get("id", ""),
            "status": summary.get("status", "unknown"),
            "stage": summary.get("stage", "unknown"),
            "message": summary.get("message", ""),
            "started_at": summary.get("started_at", ""),
            "finished_at": summary.get("finished_at", ""),
            "duration_ms": summary.get("duration_ms", 0),
            "return_code": summary.get("return_code"),
            "validation_status": summary.get("validation_status", VALIDATION_STATUS_UNKNOWN),
            "configuration_status": summary.get(
                "configuration_status",
                CONFIGURATION_SNAPSHOT_STATUS_FAILED,
            ),
            "artifact_count": summary.get("artifact_count", 0),
            "failed_artifact_count": summary.get("failed_artifact_count", 0),
            "report_path": execution_report.get("report_path", ""),
        }

    def _collect_json_artifacts(
        self,
        script_path: Path,
        configuration_snapshot: dict,
        execution_started_at: datetime,
    ) -> list[dict]:
        output_directories = self._resolve_artifact_output_directories(
            script_path=script_path,
            configuration_snapshot=configuration_snapshot,
        )
        artifacts = []

        for output_directory in output_directories:
            if not output_directory.is_dir():
                continue

            for artifact_path in sorted(output_directory.glob(JSON_FILE_PATTERN)):
                modified_at = datetime.fromtimestamp(
                    artifact_path.stat().st_mtime,
                    tz=timezone.utc,
                )

                if modified_at < execution_started_at:
                    continue

                artifacts.append(
                    self._build_json_artifact(
                        artifact_path,
                        modified_at,
                    )
                )

        return artifacts

    def _resolve_artifact_output_directories(
        self,
        script_path: Path,
        configuration_snapshot: dict,
    ) -> list[Path]:
        output_directories = [
            script_path.parent / self.task_artifact_output_directory_name,
        ]
        configuration_content = configuration_snapshot.get("content")

        if isinstance(configuration_content, dict):
            for key in ("outputPath", "outputDirectory", "artifactOutputPath"):
                configured_output_directory = configuration_content.get(key)

                if not configured_output_directory:
                    continue

                try:
                    output_directories.append(
                        self._resolve_project_relative_directory_path(
                            configured_output_directory,
                        )
                    )
                except (FileNotFoundError, ValueError):
                    continue

        return self._deduplicate_paths(output_directories)

    def _build_json_artifact(
        self,
        artifact_path: Path,
        modified_at: datetime,
    ) -> dict:
        artifact = {
            "name": artifact_path.name,
            "path": self._to_project_relative_path(artifact_path),
            "type": "json",
            "modified_at": modified_at.isoformat(),
            "status": ARTIFACT_STATUS_AVAILABLE,
            "content": None,
            "summary": None,
        }

        try:
            content = json.loads(
                artifact_path.read_text(
                    encoding="utf-8",
                )
            )
            artifact["content"] = content
            artifact["summary"] = self._extract_artifact_summary(content)
        except (OSError, json.JSONDecodeError) as error:
            artifact["status"] = ARTIFACT_STATUS_FAILED
            artifact["error"] = str(error)

        return artifact

    def _extract_artifact_summary(self, content: object) -> dict | None:
        if not isinstance(content, dict):
            return None

        summary = content.get("summary")

        if isinstance(summary, dict):
            return summary

        return None

    def _resolve_output_directory(self, output_directory) -> Path:
        if output_directory is None:
            return self.project_root / self.task_artifact_output_directory_name

        candidate_path = Path(output_directory)

        if not candidate_path.is_absolute():
            candidate_path = self.project_root / candidate_path

        candidate_path = candidate_path.resolve()

        try:
            candidate_path.relative_to(self.project_root)
        except ValueError as error:
            raise ValueError("The execution report output path escapes the project root.") from error

        return candidate_path

    def _resolve_project_relative_file_path(self, relative_path: str) -> Path:
        candidate_path = (self.project_root / str(relative_path or "")).resolve()

        try:
            candidate_path.relative_to(self.project_root)
        except ValueError as error:
            raise ValueError("The path escapes the project root.") from error

        if not candidate_path.is_file():
            raise FileNotFoundError("The file does not exist.")

        return candidate_path

    def _resolve_project_relative_directory_path(self, relative_path: str) -> Path:
        candidate_path = (self.project_root / str(relative_path or "")).resolve()

        try:
            candidate_path.relative_to(self.project_root)
        except ValueError as error:
            raise ValueError("The path escapes the project root.") from error

        if not candidate_path.is_dir():
            raise FileNotFoundError("The directory does not exist.")

        return candidate_path

    def _to_project_relative_path(self, path: Path) -> str:
        return path.resolve().relative_to(self.project_root).as_posix()

    def _safe_timestamp(self, timestamp: str) -> str:
        parsed = datetime.fromisoformat(timestamp)

        return parsed.strftime("%Y%m%d_%H%M%S_%f")

    def _safe_file_component(self, value: str) -> str:
        safe_value = re.sub(
            r"[^A-Za-z0-9_.-]",
            "_",
            str(value or ""),
        ).strip("._")

        return safe_value or "execution"

    def _deduplicate_paths(self, paths: list[Path]) -> list[Path]:
        unique_paths = []
        seen_paths = set()

        for path in paths:
            resolved_path = path.resolve()

            if resolved_path in seen_paths:
                continue

            seen_paths.add(resolved_path)
            unique_paths.append(resolved_path)

        return unique_paths

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _duration_ms(self, started_at: str, finished_at: str) -> int:
        start = datetime.fromisoformat(started_at)
        finish = datetime.fromisoformat(finished_at)

        return int((finish - start).total_seconds() * 1000)
