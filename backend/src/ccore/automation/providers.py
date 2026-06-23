"""
CCore execution provider and implementer implementations.

Responsibilities:
- Provide metadata-driven execution paths without coupling the UI to a concrete runtime technology.
- Keep the Provider as the lifecycle manager and the Implementer as the doer boundary.
- Execute local doers through explicit implementer abstractions.
- Return provider-independent execution result payloads for persistence.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .contracts import (
    ExecutionImplementer,
    ExecutionProvider,
    TaskExecutionContext,
    TaskExecutionResult,
)


class NoOpExecutionImplementer(ExecutionImplementer):
    def execute(self, context: TaskExecutionContext) -> dict:
        return {
            "summary": context.configuration_elements.get(
                "resultMessage",
                "No-op implementer completed without touching the operating system.",
            ),
            "taskId": context.task_id,
            "taskName": context.task_name,
            "providerId": context.execution_provider_id,
            "providerLabel": context.provider_label,
            "implementerTypeId": context.execution_implementer_type_id,
            "implementerTypeLabel": context.implementer_type_label,
            "targetId": context.execution_target_id,
            "targetLabel": context.target_label,
            "targetReference": context.target_reference,
            "configurationId": context.execution_configuration_id,
            "configurationLabel": context.configuration_label,
            "configurationElements": context.configuration_elements,
        }


class PythonScriptExecutionImplementer(ExecutionImplementer):
    """Run a metadata-selected Python script through the local Python interpreter."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or _resolve_project_root()

    def execute(self, context: TaskExecutionContext) -> dict:
        script_path = self._resolve_script_path(context.target_reference)
        payload = self._build_payload(context=context, script_path=script_path)

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            prefix="ccore_execution_",
            encoding="utf-8",
            delete=False,
        ) as config_file:
            json.dump(payload, config_file, indent=4)
            config_path = Path(config_file.name)

        try:
            completed_process = subprocess.run(
                [sys.executable, str(script_path), "--config", str(config_path)],
                cwd=str(self.project_root),
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            config_path.unlink(missing_ok=True)

        output_payload = self._parse_script_output(completed_process.stdout)
        outcome = {
            "summary": "Python script execution completed."
            if completed_process.returncode == 0
            else "Python script execution failed.",
            "returnCode": completed_process.returncode,
            "scriptPath": str(script_path),
            "targetReference": context.target_reference,
            "stdout": completed_process.stdout,
            "stderr": completed_process.stderr,
            "output": output_payload,
            "configurationElements": context.configuration_elements,
        }

        if completed_process.returncode != 0:
            raise RuntimeError(
                "Python script execution failed with return code "
                f"{completed_process.returncode}: {completed_process.stderr.strip()}"
            )

        return outcome

    def _resolve_script_path(self, target_reference: str) -> Path:
        if not target_reference or not target_reference.strip():
            raise ValueError("Execution target reference is required for Python script execution.")

        raw_path = Path(target_reference.strip())
        script_path = raw_path if raw_path.is_absolute() else self.project_root / raw_path
        script_path = script_path.resolve()
        project_root = self.project_root.resolve()

        if project_root not in script_path.parents and script_path != project_root:
            raise ValueError("Execution target reference must resolve inside the project root.")
        if not script_path.is_file():
            raise FileNotFoundError(f"Execution target script was not found: {script_path}")
        if script_path.suffix.lower() != ".py":
            raise ValueError(f"Execution target is not a Python script: {script_path}")

        return script_path

    def _build_payload(self, context: TaskExecutionContext, script_path: Path) -> dict[str, Any]:
        return {
            "task": {
                "taskId": context.task_id,
                "taskName": context.task_name,
                "taskType": context.task_type,
            },
            "runtime": {
                "providerId": context.execution_provider_id,
                "providerLabel": context.provider_label,
                "implementerTypeId": context.execution_implementer_type_id,
                "implementerTypeLabel": context.implementer_type_label,
                "targetId": context.execution_target_id,
                "targetLabel": context.target_label,
                "targetReference": context.target_reference,
                "resolvedTargetPath": str(script_path),
                "configurationId": context.execution_configuration_id,
                "configurationLabel": context.configuration_label,
                "configurationDescription": context.configuration_description,
            },
            "configurationElements": context.configuration_elements,
            "inputPayload": context.input_payload,
            "requestedBy": context.requested_by,
        }

    def _parse_script_output(self, stdout: str) -> dict[str, Any] | None:
        if not stdout or not stdout.strip():
            return None

        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        for line in reversed(lines):
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
        return None


class LocalExecutionProvider(ExecutionProvider):
    def run(
        self,
        context: TaskExecutionContext,
        implementer: ExecutionImplementer,
    ) -> TaskExecutionResult:
        try:
            outcome = implementer.execute(context)
            return TaskExecutionResult(
                task_id=context.task_id,
                status="COMPLETED",
                message="Task execution completed successfully.",
                provider_name=context.provider_label,
                implementer_type_name=context.implementer_type_label,
                target_name=context.target_label,
                configuration_name=context.configuration_label,
                execution_details={
                    "outcome": outcome,
                },
            )
        except Exception as exc:
            return TaskExecutionResult(
                task_id=context.task_id,
                status="FAILED",
                message=f"Task execution failed: {str(exc)}",
                provider_name=context.provider_label,
                implementer_type_name=context.implementer_type_label,
                target_name=context.target_label,
                configuration_name=context.configuration_label,
                error_details={
                    "exception": type(exc).__name__,
                    "message": str(exc),
                },
            )


def _resolve_project_root() -> Path:
    current_path = Path(__file__).resolve()
    for candidate in [current_path, *current_path.parents]:
        if (candidate / "backend").is_dir() and (candidate / "scripts").is_dir():
            return candidate
    raise RuntimeError("Could not resolve CFFP project root from automation provider path.")
