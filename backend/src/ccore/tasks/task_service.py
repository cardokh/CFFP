"""
CCore task application services.

Responsibilities:
- Coordinate CCore task CRUD use cases.
- Expose task status reference data for UI/API consumers.
- Delegate validation to CCoreTaskValidator.
- Keep API handlers independent from repository/database details.
"""

from backend.src.ccore.tasks.task import CCoreTask
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
    ):
        self.task_repository = task_repository
        self.task_validator = task_validator

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

    def delete_task(self, task_id: str) -> bool:
        self.task_validator.validate_task_id(task_id)

        return self.task_repository.delete_task(task_id)


class CCoreTaskStatusService:
    def __init__(self, status_repository: CCoreTaskStatusRepositoryProtocol):
        self.status_repository = status_repository

    def get_all_statuses(self) -> list[CCoreTaskStatus]:
        return self.status_repository.find_all_statuses()
