"""Factory task runner use case."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .interfaces.execution_provider import IExecutionProvider
from .interfaces.task_repository import ITaskRepository
from .task_execution_models import FactoryTaskExecutionRequest
from .task_models import FactoryRunnerResult, FactoryTask, FactoryTaskRunRecord
from .task_prompt_compiler import FactoryTaskPromptCompiler


@dataclass(frozen=True)
class FactoryTaskRunner:
    """Executes pending Factory tasks through injected contracts."""

    task_repository: ITaskRepository
    execution_provider: IExecutionProvider
    prompt_compiler: FactoryTaskPromptCompiler

    def run_pending_tasks(self) -> FactoryRunnerResult:
        """Discover and execute pending Factory tasks."""

        self.task_repository.initialize_schema()
        pending_tasks = self.task_repository.find_pending_tasks()
        records: list[FactoryTaskRunRecord] = []

        for task in pending_tasks:
            records.append(self._execute_task(task))

        return FactoryRunnerResult(
            discovered_count=len(pending_tasks),
            executed_count=len(records),
            completed_count=sum(1 for record in records if record.status == "COMPLETED"),
            failed_count=sum(1 for record in records if record.status == "FAILED"),
            task_runs=tuple(records),
        )

    def _execute_task(self, task: FactoryTask) -> FactoryTaskRunRecord:
        try:
            request = self._build_execution_request(task)
        except ValueError as error:
            self.task_repository.mark_failed(task.task_id, str(error))
            return FactoryTaskRunRecord(
                task_id=task.task_id,
                name=task.name,
                status="FAILED",
                message=str(error),
            )

        self.task_repository.mark_running(task.task_id)
        try:
            result = self.execution_provider.execute(request)
        except Exception as error:  # noqa: BLE001 - task status must capture provider failures.
            error_message = str(error)
            self.task_repository.mark_failed(task.task_id, error_message)
            return FactoryTaskRunRecord(
                task_id=task.task_id,
                name=task.name,
                status="FAILED",
                message=error_message,
            )

        if result.success:
            self.task_repository.mark_completed(task.task_id)
            return FactoryTaskRunRecord(
                task_id=task.task_id,
                name=task.name,
                status="COMPLETED",
                message=result.message,
            )

        self.task_repository.mark_failed(task.task_id, result.message)
        return FactoryTaskRunRecord(
            task_id=task.task_id,
            name=task.name,
            status="FAILED",
            message=result.message,
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
