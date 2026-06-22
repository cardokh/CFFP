"""
CCore task validator.

Responsibilities:
- Validate task domain objects before repository operations.
- Keep validation rules out of route handlers and repositories.
"""

from src.core.tasks.task import CCoreTask
from src.core.tasks.task_messages import (
    CCORE_TASK_INVALID_ID_MESSAGE,
    CCORE_TASK_NAME_REQUIRED_MESSAGE,
    CCORE_TASK_STATUS_REQUIRED_MESSAGE,
)


class CCoreTaskValidator:
    def validate_task_id(self, task_id: str | None) -> None:
        if not task_id or not str(task_id).strip():
            raise ValueError(CCORE_TASK_INVALID_ID_MESSAGE)

    def validate_create_task(self, task: CCoreTask) -> None:
        self._validate_task_name(task.task_name)
        self._validate_task_status(task.status)

    def validate_update_task(self, task: CCoreTask) -> None:
        self.validate_task_id(task.task_id)
        self._validate_task_name(task.task_name)
        self._validate_task_status(task.status)

    def _validate_task_name(self, task_name: str | None) -> None:
        if not task_name or not str(task_name).strip():
            raise ValueError(CCORE_TASK_NAME_REQUIRED_MESSAGE)

    def _validate_task_status(self, status: str | None) -> None:
        if not status or not str(status).strip():
            raise ValueError(CCORE_TASK_STATUS_REQUIRED_MESSAGE)
