"""
CCore task execution domain objects.

Responsibilities:
- Represent one execution run of a registered CCore task.
- Keep task definitions separate from task execution instances.
- Represent execution provider and implementer lookup metadata.
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
class CCoreExecutionImplementer:
    execution_implementer_id: int
    implementer_label: str
    sort_order: int


@dataclass(frozen=True)
class CCoreTaskExecution:
    execution_id: str | None
    task_id: str
    execution_status_id: int
    execution_provider_id: int
    execution_implementer_id: int
    status_label: str | None = None
    provider_label: str | None = None
    implementer_label: str | None = None
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
