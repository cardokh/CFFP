"""
CCore task application service.

Responsibilities:
- Coordinate CCore task CRUD use cases.
- Delegate validation to CCoreTaskValidator.
- Keep API handlers independent from repository/database details.
"""

from src.core.tasks.task import CCoreTask


class CCoreTaskService:
    def __init__(
        self,
        task_repository,
        task_validator,
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
