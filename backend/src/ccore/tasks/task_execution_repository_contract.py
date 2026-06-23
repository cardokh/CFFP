"""
CCore task execution repository contracts.

Responsibilities:
- Define repository interfaces for task execution persistence.
- Define repository interfaces for execution runtime metadata.
- Keep execution services dependent on abstractions rather than concrete PostgreSQL repositories.
"""

from typing import Protocol

from backend.src.ccore.tasks.task_execution import (
    CCoreExecutionConfiguration,
    CCoreExecutionConfigurationElement,
    CCoreExecutionImplementerType,
    CCoreExecutionProvider,
    CCoreExecutionTarget,
    CCoreTaskExecution,
)


class CCoreTaskExecutionRepositoryProtocol(Protocol):
    def create_execution(self, execution: CCoreTaskExecution) -> CCoreTaskExecution:
        """Persist one task execution record."""

    def update_execution_status(self, execution_id: str, execution_status_id: int) -> CCoreTaskExecution | None:
        """Update the lifecycle status for one task execution."""

    def update_execution_snapshots(self, execution_id: str, configuration_snapshot: dict, validation_snapshot: dict) -> CCoreTaskExecution | None:
        """Persist configuration and validation snapshots for one task execution."""

    def update_execution_result(self, execution_id: str, execution_status_id: int, execution_report: dict, error_details: dict | None = None) -> CCoreTaskExecution | None:
        """Persist the final lifecycle result and report for one task execution."""

    def find_by_execution_id(self, execution_id: str) -> CCoreTaskExecution | None:
        """Return one execution by execution identifier."""

    def find_latest_by_task_id(self, task_id: str) -> CCoreTaskExecution | None:
        """Return the latest execution for one task."""

    def find_by_task_id(self, task_id: str) -> list[CCoreTaskExecution]:
        """Return execution history for one task."""

    def find_all_execution_providers(self) -> list[CCoreExecutionProvider]:
        """Return available execution providers."""

    def find_all_execution_implementer_types(self) -> list[CCoreExecutionImplementerType]:
        """Return available execution implementer types."""

    def find_all_execution_targets(self) -> list[CCoreExecutionTarget]:
        """Return available execution targets."""

    def find_all_execution_configurations(self) -> list[CCoreExecutionConfiguration]:
        """Return available execution configurations."""

    def find_execution_configuration_elements_by_configuration_id(self, execution_configuration_id: int) -> list[CCoreExecutionConfigurationElement]:
        """Return configuration elements for one execution configuration."""

    def find_execution_provider_by_id(self, execution_provider_id: int) -> CCoreExecutionProvider | None:
        """Return one execution provider by identifier."""

    def find_execution_implementer_type_by_id(self, execution_implementer_type_id: int) -> CCoreExecutionImplementerType | None:
        """Return one execution implementer type by identifier."""

    def find_execution_target_by_id(self, execution_target_id: int) -> CCoreExecutionTarget | None:
        """Return one execution target by identifier."""

    def find_execution_configuration_by_id(self, execution_configuration_id: int) -> CCoreExecutionConfiguration | None:
        """Return one execution configuration by identifier."""
