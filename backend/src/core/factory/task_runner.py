"""Factory task runner use case."""

from __future__ import annotations

from dataclasses import dataclass

from .task_models import FactoryRunnerResult
from .interfaces.task_repository import ITaskRepository


@dataclass(frozen=True)
class FactoryTaskRunner:
    """Loads pending Factory tasks through the repository contract."""

    task_repository: ITaskRepository

    def run_pending_tasks(self) -> FactoryRunnerResult:
        """Discover pending tasks from persistence.

        Iteration 1 establishes SQL-backed discovery only. Execution and status
        transitions are introduced in the next iteration.
        """

        self.task_repository.initialize_schema()
        pending_tasks = self.task_repository.find_pending_tasks()
        return FactoryRunnerResult(
            discovered_count=len(pending_tasks),
            pending_tasks=pending_tasks,
        )
