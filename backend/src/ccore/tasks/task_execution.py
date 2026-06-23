"""
CCore task execution domain objects.

Responsibilities:
- Represent one execution run of a registered CCore task.
- Keep task definitions separate from task execution instances.
- Represent execution provider, implementer type, target, and configuration metadata.
- Carry execution payloads, snapshots, reports, and lifecycle timestamps.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CCoreExecutionProvider:
    execution_provider_id: int
    provider_label: str
    sort_order: int


@dataclass(frozen=True)
class CCoreExecutionImplementerType:
    execution_implementer_type_id: int
    implementer_type_label: str
    sort_order: int


@dataclass(frozen=True)
class CCoreExecutionTarget:
    execution_target_id: int
    execution_implementer_type_id: int
    target_label: str
    target_reference: str
    sort_order: int


@dataclass(frozen=True)
class CCoreExecutionConfiguration:
    execution_configuration_id: int
    execution_target_id: int
    configuration_label: str
    configuration_description: str | None
    sort_order: int


@dataclass(frozen=True)
class CCoreExecutionConfigurationElement:
    execution_configuration_element_id: int
    execution_configuration_id: int
    element_name: str
    element_value: str
    sort_order: int


@dataclass(frozen=True)
class CCoreTaskExecution:
    execution_id: str | None
    task_id: str
    execution_status_id: int
    execution_provider_id: int
    execution_implementer_type_id: int
    execution_target_id: int
    execution_configuration_id: int
    status_label: str | None = None
    provider_label: str | None = None
    implementer_type_label: str | None = None
    target_label: str | None = None
    target_reference: str | None = None
    configuration_label: str | None = None
    configuration_description: str | None = None
    requested_by: str = "system"
    input_payload: dict[str, Any] | None = None
    configuration_snapshot: dict[str, Any] | None = None
    validation_snapshot: dict[str, Any] | None = None
    execution_report: dict[str, Any] | None = None
    error_details: dict[str, Any] | None = None
    started_at: str | None = None
    completed_at: str | None = None
    failed_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
