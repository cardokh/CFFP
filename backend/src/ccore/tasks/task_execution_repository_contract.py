"""
CCore task execution repository contracts.

Responsibilities:
- Define repository interfaces for task execution persistence.
- Keep execution services dependent on abstractions rather than concrete PostgreSQL repositories.
"""

from typing import Protocol

from backend.src.ccore.tasks.task_execution import CCoreTaskExecution


class CCoreTaskExecutionRepositoryProtocol(Protocol):
    def create_execution(self, execution: CCoreTaskExecution) -> CCoreTaskExecution:
        """Persist one completed task execution."""

    def find_latest_by_task_id(self, task_id: str) -> CCoreTaskExecution | None:
        """Return the latest execution for one task."""

    def find_by_task_id(self, task_id: str) -> list[CCoreTaskExecution]:
        """Return execution history for one task."""
