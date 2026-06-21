"""Factory SQL task repository tests."""

from __future__ import annotations

from pathlib import Path

from src.core.factory.sql_task_repository import SqlTaskRepository
from src.core.factory.task_models import FactoryTask
from src.core.factory.task_status import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
)
from src.core.infrastructure.database import DatabaseManager


def build_repository(database_path: Path) -> SqlTaskRepository:
    repository = SqlTaskRepository(DatabaseManager(str(database_path)))
    repository.initialize_schema()
    return repository


def test_repository_creates_and_discovers_pending_tasks(tmp_path) -> None:
    repository = build_repository(tmp_path / "factory.db")

    repository.upsert_task(
        FactoryTask(
            task_id="task.two",
            name="Second Task",
            description="Second pending task.",
            status=TASK_STATUS_PENDING,
            task_definition_path="tasks/second.json",
            priority=20,
        )
    )
    repository.upsert_task(
        FactoryTask(
            task_id="task.one",
            name="First Task",
            description="First pending task.",
            status=TASK_STATUS_PENDING,
            task_definition_path="tasks/first.json",
            priority=10,
        )
    )

    pending_tasks = repository.find_pending_tasks()

    assert [task.task_id for task in pending_tasks] == ["task.one", "task.two"]
    assert pending_tasks[0].status == TASK_STATUS_PENDING


def test_repository_excludes_non_pending_tasks(tmp_path) -> None:
    repository = build_repository(tmp_path / "factory.db")

    repository.upsert_task(
        FactoryTask(
            task_id="task.done",
            name="Completed Task",
            description="Already completed.",
            status=TASK_STATUS_COMPLETED,
            task_definition_path="tasks/done.json",
            priority=10,
        )
    )

    assert repository.find_pending_tasks() == ()


def test_repository_updates_task_lifecycle_state(tmp_path) -> None:
    repository = build_repository(tmp_path / "factory.db")
    repository.upsert_task(
        FactoryTask(
            task_id="task.lifecycle",
            name="Lifecycle Task",
            description="Lifecycle state test.",
            status=TASK_STATUS_PENDING,
            task_definition_path="tasks/lifecycle.json",
            priority=10,
        )
    )

    repository.mark_running("task.lifecycle")
    assert repository.find_pending_tasks() == ()

    repository.upsert_task(
        FactoryTask(
            task_id="task.lifecycle",
            name="Lifecycle Task",
            description="Lifecycle state test.",
            status=TASK_STATUS_PENDING,
            task_definition_path="tasks/lifecycle.json",
            priority=10,
        )
    )
    repository.mark_failed("task.lifecycle", "boom")
    assert repository.find_pending_tasks() == ()

    repository.upsert_task(
        FactoryTask(
            task_id="task.lifecycle",
            name="Lifecycle Task",
            description="Lifecycle state test.",
            status=TASK_STATUS_PENDING,
            task_definition_path="tasks/lifecycle.json",
            priority=10,
        )
    )
    repository.mark_completed("task.lifecycle")
    assert repository.find_pending_tasks() == ()
