"""
CCore task execution domain objects.

Responsibilities:
- Represent one execution run of a registered CCore task.
- Keep task definitions separate from task execution instances.
- Carry execution payloads, snapshots, reports, and lifecycle timestamps.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CCoreTaskExecution:
    execution_id: str | None
    task_id: str
    status_code: str
    status_label: str | None = None
    provider_profile: str = "prefect"
    execution_mode: str = "manual"
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
