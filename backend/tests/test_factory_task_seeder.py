"""Factory task seeder tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.core.factory.task_models import FactoryTask
from src.core.factory.task_seed_models import FactoryTaskSeed
from src.core.factory.task_seeder import FactoryTaskSeeder
from src.core.factory.task_status import TASK_STATUS_PENDING


@dataclass
class InMemoryTaskRepository:
    initialized: bool = False
    upserted_tasks: list[FactoryTask] = field(default_factory=list)

    def initialize_schema(self) -> None:
        self.initialized = True

    def find_pending_tasks(self) -> tuple[FactoryTask, ...]:
        return tuple(self.upserted_tasks)

    def upsert_task(self, task: FactoryTask) -> None:
        self.upserted_tasks.append(task)

    def mark_running(self, task_id: str) -> None:
        raise NotImplementedError

    def mark_completed(self, task_id: str) -> None:
        raise NotImplementedError

    def mark_failed(self, task_id: str, error_message: str) -> None:
        raise NotImplementedError


def test_seeder_upserts_pending_tasks() -> None:
    repository = InMemoryTaskRepository()
    seeds = (
        FactoryTaskSeed(
            task_id="factory.seed",
            name="Seed Task",
            description="Seeded task.",
            task_definition_path="tasks/seed.json",
            priority=10,
            payload='{"scope": "test"}',
        ),
    )

    result = FactoryTaskSeeder(task_repository=repository).seed_tasks(seeds)

    assert repository.initialized is True
    assert result == {"seeded_count": 1, "task_ids": ["factory.seed"]}
    assert repository.upserted_tasks[0].status == TASK_STATUS_PENDING
    assert repository.upserted_tasks[0].task_definition_path == "tasks/seed.json"
    assert repository.upserted_tasks[0].payload == '{"scope": "test"}'
