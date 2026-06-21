"""Factory task seeding use case."""

from __future__ import annotations

from dataclasses import dataclass

from .task_models import FactoryTask
from .interfaces.task_repository import ITaskRepository
from .task_seed_models import FactoryTaskSeed
from .task_status import TASK_STATUS_PENDING


@dataclass(frozen=True)
class FactoryTaskSeeder:
    """Seeds pending Factory tasks through the task repository contract."""

    task_repository: ITaskRepository

    def seed_tasks(self, seeds: tuple[FactoryTaskSeed, ...]) -> dict[str, object]:
        """Seed configured Factory tasks as pending tasks."""

        self.task_repository.initialize_schema()
        for seed in seeds:
            self.task_repository.upsert_task(
                FactoryTask(
                    task_id=seed.task_id,
                    name=seed.name,
                    description=seed.description,
                    status=TASK_STATUS_PENDING,
                    task_definition_path=seed.task_definition_path,
                    priority=seed.priority,
                    payload=seed.payload,
                )
            )

        return {
            "seeded_count": len(seeds),
            "task_ids": [seed.task_id for seed in seeds],
        }
