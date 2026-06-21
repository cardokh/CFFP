"""Factory task execution report assembly."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from .reporting import utc_now_iso
from .task_execution_models import FactoryTaskExecutionRequest, FactoryTaskExecutionResult
from .task_models import FactoryTask
from .task_report_writer import FactoryTaskReportWriter
from .validation import FactoryValidationResult


@dataclass(frozen=True)
class FactoryTaskExecutionReportBuilder:
    """Builds and writes one Factory task execution report."""

    report_writer: FactoryTaskReportWriter

    def write_report(
        self,
        *,
        execution_id: str,
        task: FactoryTask,
        started_at: str,
        started_time: float,
        status: str,
        message: str,
        payload: dict[str, Any],
        request: FactoryTaskExecutionRequest | None,
        result: FactoryTaskExecutionResult | None,
        validation_result: FactoryValidationResult | None,
        artifact_path: str | None,
    ) -> str:
        """Write an execution report and return its path."""

        report = self.build_report(
            execution_id=execution_id,
            task=task,
            started_at=started_at,
            started_time=started_time,
            status=status,
            message=message,
            payload=payload,
            request=request,
            result=result,
            validation_result=validation_result,
            artifact_path=artifact_path,
        )
        report_record = self.report_writer.write_report(
            execution_id=execution_id,
            task_id=task.task_id,
            report=report,
        )
        return report_record.path

    def build_report(
        self,
        *,
        execution_id: str,
        task: FactoryTask,
        started_at: str,
        started_time: float,
        status: str,
        message: str,
        payload: dict[str, Any],
        request: FactoryTaskExecutionRequest | None,
        result: FactoryTaskExecutionResult | None,
        validation_result: FactoryValidationResult | None,
        artifact_path: str | None,
    ) -> dict[str, Any]:
        """Create a serializable execution report."""

        return {
            "execution_id": execution_id,
            "task_id": task.task_id,
            "task_name": task.name,
            "status": status,
            "message": message,
            "started_at": started_at,
            "completed_at": utc_now_iso(),
            "duration_ms": int((time.perf_counter() - started_time) * 1000),
            "task_definition_path": task.task_definition_path,
            "priority": task.priority,
            "payload_keys": sorted(payload.keys()),
            "metrics": _metrics(request, result),
            "validation": validation_result.to_dict() if validation_result else None,
            "artifact_path": artifact_path,
            "provider_result": result.to_dict() if result else None,
        }


def _metrics(
    request: FactoryTaskExecutionRequest | None,
    result: FactoryTaskExecutionResult | None,
) -> dict[str, int]:
    return {
        "prompt_characters": len(request.prompt) if request else 0,
        "system_instruction_characters": len(request.system_instruction or "") if request else 0,
        "context_file_count": request.context_file_count if request else 0,
        "artifact_characters": len(result.artifact_text or "") if result else 0,
    }
