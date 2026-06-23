"""
CCore task application services.

Responsibilities:
- Coordinate CCore task CRUD use cases.
- Expose task status reference data for UI/API consumers.
- Provide read access to task execution history through the execution repository.
- Keep API handlers independent from repository/database details.
"""

from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_execution import CCoreTaskExecution
from backend.src.ccore.tasks.task_repository_contract import (
    CCoreTaskRepositoryProtocol,
    CCoreTaskStatusRepositoryProtocol,
)
from backend.src.ccore.tasks.task_status import CCoreTaskStatus
from backend.src.ccore.tasks.task_validator import CCoreTaskValidator


class CCoreTaskService:
    def __init__(
        self,
        task_repository: CCoreTaskRepositoryProtocol,
        task_validator: CCoreTaskValidator,
        task_execution_repository=None,
    ):
        self.task_repository = task_repository
        self.task_validator = task_validator
        self.task_execution_repository = task_execution_repository

    def get_all_tasks(self) -> list[CCoreTask]:
        return self.task_repository.find_all_tasks()

    def get_task_by_id(self, task_id: str) -> CCoreTask | None:
        self.task_validator.validate_task_id(task_id)

        return self.task_repository.find_by_id(task_id)

    def create_task(self, task: CCoreTask) -> CCoreTask:
        self.task_validator.validate_create_task(task)

        return self.task_repository.create_task(task)

    def update_task(self, task: CCoreTask) -> CCoreTask | None:
        self.task_validator.validate_update_task(task)

        return self.task_repository.update_task(task)

    def update_task_status(
        self,
        task_id: str,
        status_id: int,
    ) -> CCoreTask | None:
        self.task_validator.validate_task_id(task_id)

        if not self.task_validator.status_repository.status_exists(status_id):
            raise ValueError(f"Invalid CCore task status code: {status_id}")

        return self.task_repository.update_task_status(task_id, status_id)

    def delete_task(self, task_id: str) -> bool:
        self.task_validator.validate_task_id(task_id)

        return self.task_repository.delete_task(task_id)

    def get_latest_execution(self, task_id: str) -> CCoreTaskExecution | None:
        self.task_validator.validate_task_id(task_id)
        self._validate_execution_repository_configured()

        return self.task_execution_repository.find_latest_by_task_id(task_id)

    def get_execution_history(self, task_id: str) -> list[CCoreTaskExecution]:
        self.task_validator.validate_task_id(task_id)
        self._validate_execution_repository_configured()

        return self.task_execution_repository.find_by_task_id(task_id)

    def _validate_execution_repository_configured(self) -> None:
        if self.task_execution_repository is None:
            raise ValueError("CCore task execution repository is not configured.")


class CCoreTaskStatusService:
    def __init__(self, status_repository: CCoreTaskStatusRepositoryProtocol):
        self.status_repository = status_repository

    def get_all_statuses(self) -> list[CCoreTaskStatus]:
        return self.status_repository.find_all_statuses()
