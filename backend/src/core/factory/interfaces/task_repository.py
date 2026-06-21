"""Factory task repository interface."""

from __future__ import annotations

from typing import Protocol

from src.core.factory.task_models import FactoryTask


class ITaskRepository(Protocol):
    """Persistence contract for Factory task lifecycle state."""

    def initialize_schema(self) -> None:
        """Create required persistence structures if they do not exist."""

    def find_pending_tasks(self) -> tuple[FactoryTask, ...]:
        """Return pending tasks ordered for execution."""

    def upsert_task(self, task: FactoryTask) -> None:
        """Create or update one task."""

    def mark_running(self, task_id: str) -> None:
        """Mark one task as running."""

    def mark_completed(self, task_id: str) -> None:
        """Mark one task as completed."""

    def mark_failed(self, task_id: str, error_message: str) -> None:
        """Mark one task as failed."""
