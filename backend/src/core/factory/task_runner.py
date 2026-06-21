"""Factory task runner use case."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .interfaces.execution_provider import IExecutionProvider
from .interfaces.task_repository import ITaskRepository
from .task_artifact_writer import FactoryTaskArtifactWriter
from .task_execution_report_builder import FactoryTaskExecutionReportBuilder
from .task_executor import FactoryTaskExecutor
from .task_models import FactoryRunnerResult, FactoryTaskRunRecord
from .task_prompt_compiler import FactoryTaskPromptCompiler
from .task_report_writer import FactoryTaskReportWriter
from .task_status import TASK_STATUS_COMPLETED, TASK_STATUS_FAILED
from .validation import FactoryOutputValidator


@dataclass(frozen=True)
class FactoryTaskRunner:
    """Discovers pending Factory tasks and delegates one-task execution."""

    task_repository: ITaskRepository
    execution_provider: IExecutionProvider
    prompt_compiler: FactoryTaskPromptCompiler
    output_validator: FactoryOutputValidator = field(default_factory=FactoryOutputValidator)
    artifact_writer: FactoryTaskArtifactWriter = field(
        default_factory=lambda: FactoryTaskArtifactWriter(Path("runtime/factory/output"))
    )
    report_writer: FactoryTaskReportWriter = field(
        default_factory=lambda: FactoryTaskReportWriter(Path("runtime/factory/reports"))
    )

    def run_pending_tasks(self) -> FactoryRunnerResult:
        """Discover and execute pending Factory tasks."""

        self.task_repository.initialize_schema()
        pending_tasks = self.task_repository.find_pending_tasks()
        executor = self._build_executor()
        records = tuple(executor.execute_task(task) for task in pending_tasks)

        return FactoryRunnerResult(
            discovered_count=len(pending_tasks),
            executed_count=len(records),
            completed_count=_count_status(records, TASK_STATUS_COMPLETED),
            failed_count=_count_status(records, TASK_STATUS_FAILED),
            task_runs=records,
        )

    def _build_executor(self) -> FactoryTaskExecutor:
        return FactoryTaskExecutor(
            task_repository=self.task_repository,
            execution_provider=self.execution_provider,
            prompt_compiler=self.prompt_compiler,
            output_validator=self.output_validator,
            artifact_writer=self.artifact_writer,
            report_builder=FactoryTaskExecutionReportBuilder(self.report_writer),
        )


def _count_status(records: tuple[FactoryTaskRunRecord, ...], status: str) -> int:
    return sum(1 for record in records if record.status == status)
