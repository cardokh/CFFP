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
        """Persist one task execution record."""

    def update_execution_status(
        self,
        execution_id: str,
        status_code: str,
    ) -> CCoreTaskExecution | None:
        """Update the lifecycle status for one task execution."""

    def update_execution_snapshots(
        self,
        execution_id: str,
        configuration_snapshot: dict,
        validation_snapshot: dict,
    ) -> CCoreTaskExecution | None:
        """Persist configuration and validation snapshots for one task execution."""

    def update_execution_result(
        self,
        execution_id: str,
        status_code: str,
        execution_report: dict,
        error_details: dict | None = None,
    ) -> CCoreTaskExecution | None:
        """Persist the final lifecycle result and report for one task execution."""

    def find_by_execution_id(self, execution_id: str) -> CCoreTaskExecution | None:
        """Return one execution by execution identifier."""

    def find_latest_by_task_id(self, task_id: str) -> CCoreTaskExecution | None:
        """Return the latest execution for one task."""

    def find_by_task_id(self, task_id: str) -> list[CCoreTaskExecution]:
        """Return execution history for one task."""
