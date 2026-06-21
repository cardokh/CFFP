"""Factory task executor use case."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

from .interfaces.execution_provider import IExecutionProvider
from .interfaces.task_repository import ITaskRepository
from .reporting import utc_now_iso
from .task_artifact_writer import FactoryTaskArtifactWriter
from .task_execution_models import FactoryTaskExecutionRequest, FactoryTaskExecutionResult
from .task_execution_report_builder import FactoryTaskExecutionReportBuilder
from .task_models import FactoryTask, FactoryTaskRunRecord
from .task_prompt_compiler import FactoryTaskPromptCompiler
from .task_status import TASK_STATUS_COMPLETED, TASK_STATUS_FAILED
from .validation import FactoryOutputValidator, FactoryValidationResult


@dataclass(frozen=True)
class FactoryTaskExecutor:
    """Executes one Factory task through injected contracts."""

    task_repository: ITaskRepository
    execution_provider: IExecutionProvider
    prompt_compiler: FactoryTaskPromptCompiler
    output_validator: FactoryOutputValidator
    artifact_writer: FactoryTaskArtifactWriter
    report_builder: FactoryTaskExecutionReportBuilder

    def execute_task(self, task: FactoryTask) -> FactoryTaskRunRecord:
        """Execute one pending Factory task."""

        execution_id = str(uuid.uuid4())
        started_at = utc_now_iso()
        started_time = time.perf_counter()
        payload: dict[str, Any] = {}
        request: FactoryTaskExecutionRequest | None = None
        result: FactoryTaskExecutionResult | None = None
        validation_result: FactoryValidationResult | None = None
        artifact_path: str | None = None

        try:
            request = self._build_execution_request(task)
            payload = request.payload
        except ValueError as error:
            return self._fail_task(
                task=task,
                execution_id=execution_id,
                started_at=started_at,
                started_time=started_time,
                message=str(error),
                payload=payload,
                request=request,
                result=result,
                validation_result=validation_result,
                artifact_path=artifact_path,
            )

        self.task_repository.mark_running(task.task_id)
        try:
            result = self.execution_provider.execute(request)
        except Exception as error:  # noqa: BLE001 - task status must capture provider failures.
            return self._fail_task(
                task=task,
                execution_id=execution_id,
                started_at=started_at,
                started_time=started_time,
                message=str(error),
                payload=payload,
                request=request,
                result=result,
                validation_result=validation_result,
                artifact_path=artifact_path,
            )

        if not result.success:
            return self._fail_task(
                task=task,
                execution_id=execution_id,
                started_at=started_at,
                started_time=started_time,
                message=result.message,
                payload=payload,
                request=request,
                result=result,
                validation_result=validation_result,
                artifact_path=artifact_path,
            )

        validation_result = self.output_validator.validate_artifact_text(result.artifact_text)
        if not validation_result.passed:
            return self._fail_task(
                task=task,
                execution_id=execution_id,
                started_at=started_at,
                started_time=started_time,
                message=validation_result.message,
                payload=payload,
                request=request,
                result=result,
                validation_result=validation_result,
                artifact_path=artifact_path,
            )

        artifact = self.artifact_writer.write_artifact(
            execution_id=execution_id,
            task_id=task.task_id,
            artifact_text=result.artifact_text or "",
            filename=self._artifact_filename(payload),
        )
        self.task_repository.mark_completed(task.task_id)
        report_path = self.report_builder.write_report(
            execution_id=execution_id,
            task=task,
            started_at=started_at,
            started_time=started_time,
            status=TASK_STATUS_COMPLETED,
            message=result.message,
            payload=payload,
            request=request,
            result=result,
            validation_result=validation_result,
            artifact_path=artifact.path,
        )
        return FactoryTaskRunRecord(
            task_id=task.task_id,
            name=task.name,
            status=TASK_STATUS_COMPLETED,
            message=result.message,
            artifact_path=artifact.path,
            report_path=report_path,
        )

    def _fail_task(
        self,
        *,
        task: FactoryTask,
        execution_id: str,
        started_at: str,
        started_time: float,
        message: str,
        payload: dict[str, Any],
        request: FactoryTaskExecutionRequest | None,
        result: FactoryTaskExecutionResult | None,
        validation_result: FactoryValidationResult | None,
        artifact_path: str | None,
    ) -> FactoryTaskRunRecord:
        self.task_repository.mark_failed(task.task_id, message)
        report_path = self.report_builder.write_report(
            execution_id=execution_id,
            task=task,
            started_at=started_at,
            started_time=started_time,
            status=TASK_STATUS_FAILED,
            message=message,
            payload=payload,
            request=request,
            result=result,
            validation_result=validation_result,
            artifact_path=artifact_path,
        )
        return FactoryTaskRunRecord(
            task_id=task.task_id,
            name=task.name,
            status=TASK_STATUS_FAILED,
            message=message,
            report_path=report_path,
        )

    def _build_execution_request(self, task: FactoryTask) -> FactoryTaskExecutionRequest:
        payload = self._parse_payload(task.payload)
        compiled_prompt = self.prompt_compiler.compile_prompt(task, payload)
        return FactoryTaskExecutionRequest(
            task_id=task.task_id,
            name=task.name,
            task_definition_path=task.task_definition_path,
            priority=task.priority,
            payload=payload,
            prompt=compiled_prompt.prompt,
            system_instruction=compiled_prompt.system_instruction,
            context_file_count=compiled_prompt.context_file_count,
        )

    def _parse_payload(self, raw_payload: str) -> dict[str, Any]:
        try:
            parsed_payload = json.loads(raw_payload or "{}")
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid task payload JSON: {error.msg}") from error

        if not isinstance(parsed_payload, dict):
            raise ValueError("Task payload must be a JSON object.")
        return parsed_payload

    def _artifact_filename(self, payload: dict[str, Any]) -> str:
        filename = payload.get("artifact_filename") or payload.get("output_filename")
        return str(filename) if filename else "generated_summary.md"
