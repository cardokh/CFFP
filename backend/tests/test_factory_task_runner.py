"""Factory task runner tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.core.factory.task_execution_models import (
    FactoryTaskExecutionRequest,
    FactoryTaskExecutionResult,
)
from src.core.factory.task_models import FactoryTask
from src.core.factory.task_runner import FactoryTaskRunner
from src.core.factory.task_status import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
)


@dataclass
class InMemoryTaskRepository:
    pending_tasks: tuple[FactoryTask, ...]
    initialized: bool = False
    running_task_ids: list[str] = field(default_factory=list)
    completed_task_ids: list[str] = field(default_factory=list)
    failed_tasks: dict[str, str] = field(default_factory=dict)

    def initialize_schema(self) -> None:
        self.initialized = True

    def find_pending_tasks(self) -> tuple[FactoryTask, ...]:
        return self.pending_tasks

    def upsert_task(self, task: FactoryTask) -> None:
        raise NotImplementedError

    def mark_running(self, task_id: str) -> None:
        self.running_task_ids.append(task_id)

    def mark_completed(self, task_id: str) -> None:
        self.completed_task_ids.append(task_id)

    def mark_failed(self, task_id: str, error_message: str) -> None:
        self.failed_tasks[task_id] = error_message


@dataclass
class PassingExecutionProvider:
    requests: list[FactoryTaskExecutionRequest] = field(default_factory=list)

    def execute(self, request: FactoryTaskExecutionRequest) -> FactoryTaskExecutionResult:
        self.requests.append(request)
        return FactoryTaskExecutionResult(
            task_id=request.task_id,
            success=True,
            message="done",
        )


@dataclass
class FailingExecutionProvider:
    def execute(self, request: FactoryTaskExecutionRequest) -> FactoryTaskExecutionResult:
        return FactoryTaskExecutionResult(
            task_id=request.task_id,
            success=False,
            message="failed",
        )


@dataclass
class RaisingExecutionProvider:
    def execute(self, request: FactoryTaskExecutionRequest) -> FactoryTaskExecutionResult:
        raise RuntimeError("provider boom")


def build_task(payload: str = '{"scope": "test"}') -> FactoryTask:
    return FactoryTask(
        task_id="factory.example",
        name="Example Task",
        description="Example pending task.",
        status=TASK_STATUS_PENDING,
        task_definition_path="backend/src/core/factory/tasks/example.json",
        priority=10,
        payload=payload,
    )


def test_runner_executes_pending_task_and_marks_completed() -> None:
    task = build_task()
    repository = InMemoryTaskRepository(pending_tasks=(task,))
    execution_provider = PassingExecutionProvider()

    result = FactoryTaskRunner(
        task_repository=repository,
        execution_provider=execution_provider,
    ).run_pending_tasks()

    assert repository.initialized is True
    assert repository.running_task_ids == ["factory.example"]
    assert repository.completed_task_ids == ["factory.example"]
    assert repository.failed_tasks == {}
    assert execution_provider.requests[0].task_id == "factory.example"
    assert execution_provider.requests[0].payload == {"scope": "test"}
    assert result.to_dict() == {
        "discovered_count": 1,
        "executed_count": 1,
        "completed_count": 1,
        "failed_count": 0,
        "task_runs": [
            {
                "task_id": "factory.example",
                "name": "Example Task",
                "status": TASK_STATUS_COMPLETED,
                "message": "done",
            }
        ],
    }


def test_runner_marks_failed_when_execution_provider_returns_failure() -> None:
    task = build_task()
    repository = InMemoryTaskRepository(pending_tasks=(task,))

    result = FactoryTaskRunner(
        task_repository=repository,
        execution_provider=FailingExecutionProvider(),
    ).run_pending_tasks()

    assert repository.running_task_ids == ["factory.example"]
    assert repository.completed_task_ids == []
    assert repository.failed_tasks == {"factory.example": "failed"}
    assert result.failed_count == 1


def test_runner_marks_failed_when_execution_provider_raises() -> None:
    task = build_task()
    repository = InMemoryTaskRepository(pending_tasks=(task,))

    result = FactoryTaskRunner(
        task_repository=repository,
        execution_provider=RaisingExecutionProvider(),
    ).run_pending_tasks()

    assert repository.running_task_ids == ["factory.example"]
    assert repository.completed_task_ids == []
    assert repository.failed_tasks == {"factory.example": "provider boom"}
    assert result.failed_count == 1


def test_runner_marks_failed_when_payload_is_invalid_json() -> None:
    task = build_task(payload="not-json")
    repository = InMemoryTaskRepository(pending_tasks=(task,))
    execution_provider = PassingExecutionProvider()

    result = FactoryTaskRunner(
        task_repository=repository,
        execution_provider=execution_provider,
    ).run_pending_tasks()

    assert repository.running_task_ids == []
    assert repository.completed_task_ids == []
    assert repository.failed_tasks == {"factory.example": "Invalid task payload JSON: Expecting value"}
    assert execution_provider.requests == []
    assert result.failed_count == 1
