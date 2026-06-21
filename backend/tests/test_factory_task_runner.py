"""Factory task runner tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.core.factory.task_models import FactoryTask
from src.core.factory.task_runner import FactoryTaskRunner
from src.core.factory.task_status import TASK_STATUS_PENDING


@dataclass
class InMemoryTaskRepository:
    pending_tasks: tuple[FactoryTask, ...]
    initialized: bool = False
    upserted_tasks: list[FactoryTask] = field(default_factory=list)

    def initialize_schema(self) -> None:
        self.initialized = True

    def find_pending_tasks(self) -> tuple[FactoryTask, ...]:
        return self.pending_tasks

    def upsert_task(self, task: FactoryTask) -> None:
        self.upserted_tasks.append(task)

    def mark_running(self, task_id: str) -> None:
        raise AssertionError("Iteration 1 runner must not execute tasks yet.")

    def mark_completed(self, task_id: str) -> None:
        raise AssertionError("Iteration 1 runner must not execute tasks yet.")

    def mark_failed(self, task_id: str, error_message: str) -> None:
        raise AssertionError("Iteration 1 runner must not execute tasks yet.")


def test_runner_initializes_schema_and_returns_pending_tasks() -> None:
    task = FactoryTask(
        task_id="factory.example",
        name="Example Task",
        description="Example pending task.",
        status=TASK_STATUS_PENDING,
        task_definition_path="backend/src/core/factory/tasks/example.json",
        priority=10,
    )
    repository = InMemoryTaskRepository(pending_tasks=(task,))

    result = FactoryTaskRunner(task_repository=repository).run_pending_tasks()

    assert repository.initialized is True
    assert result.discovered_count == 1
    assert result.pending_tasks == (task,)
    assert result.to_dict()["pending_tasks"] == [
        {
            "task_id": "factory.example",
            "name": "Example Task",
            "status": "PENDING",
            "task_definition_path": "backend/src/core/factory/tasks/example.json",
            "priority": 10,
            "payload": '{}',
        }
    ]
