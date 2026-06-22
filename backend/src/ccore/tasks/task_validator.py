"""
CCore task validator.

Responsibilities:
- Validate task domain objects before repository operations.
- Keep validation rules out of route handlers and repositories.
- Validate lookup/reference values through repository contracts.
"""

from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_messages import (
    CCORE_TASK_INVALID_ID_MESSAGE,
    CCORE_TASK_NAME_REQUIRED_MESSAGE,
    CCORE_TASK_STATUS_INVALID_MESSAGE,
    CCORE_TASK_STATUS_REQUIRED_MESSAGE,
)
from backend.src.ccore.tasks.task_repository_contract import (
    CCoreTaskStatusRepositoryProtocol,
)


class CCoreTaskValidator:
    def __init__(self, status_repository: CCoreTaskStatusRepositoryProtocol):
        self.status_repository = status_repository

    def validate_task_id(self, task_id: str | None) -> None:
        if not task_id or not str(task_id).strip():
            raise ValueError(CCORE_TASK_INVALID_ID_MESSAGE)

    def validate_create_task(self, task: CCoreTask) -> None:
        self._validate_task_name(task.task_name)
        self._validate_task_status(task.status_code)

    def validate_update_task(self, task: CCoreTask) -> None:
        self.validate_task_id(task.task_id)
        self._validate_task_name(task.task_name)
        self._validate_task_status(task.status_code)

    def _validate_task_name(self, task_name: str | None) -> None:
        if not task_name or not str(task_name).strip():
            raise ValueError(CCORE_TASK_NAME_REQUIRED_MESSAGE)

    def _validate_task_status(self, status_code: str | None) -> None:
        if not status_code or not str(status_code).strip():
            raise ValueError(CCORE_TASK_STATUS_REQUIRED_MESSAGE)

        if not self.status_repository.status_exists(str(status_code).strip()):
            raise ValueError(CCORE_TASK_STATUS_INVALID_MESSAGE)
