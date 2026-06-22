"""
CCore task execution domain objects.

Responsibilities:
- Represent one execution of a registered CCore task.
- Keep task definitions separate from task execution instances.
- Carry execution report data produced by Automation Factory runners.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CCoreTaskExecution:
    execution_id: str | None
    task_id: str
    status_code: str
    status_label: str | None = None
    runner_code: str | None = None
    report_json: dict[str, Any] | None = None
    started_at: str | None = None
    finished_at: str | None = None
    created_at: str | None = None
