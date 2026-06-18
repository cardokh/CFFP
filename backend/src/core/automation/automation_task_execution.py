"""
Automation task execution domain objects.

Responsibilities:
- Represent one attempt to execute an automation task.
- Keep execution state separate from task registry metadata.
- Provide structured results for manual execution and future pipeline orchestration.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationTaskExecutionResult:
    execution_id: str
    task_id: str
    status: str
    stage: str
    message: str
    started_at: str
    finished_at: str
    duration_ms: int
    return_code: int | None
    stdout: str
    stderr: str
    validation: dict | None
