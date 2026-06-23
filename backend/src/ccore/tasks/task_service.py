"""
CCore task application services.

Responsibilities:
- Coordinate CCore task CRUD use cases.
- Expose task status reference data for UI/API consumers.
- Delegate validation to CCoreTaskValidator.
- Keep API handlers independent from repository/database details.
"""

from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_execution import CCoreTaskExecution
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_STATUS_BLOCKED,
)
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
        task_runner_registry=None,
    ):
        self.task_repository = task_repository
        self.task_validator = task_validator
        self.task_execution_repository = task_execution_repository
        self.task_runner_registry = task_runner_registry

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
        status_code: str,
    ) -> CCoreTask | None:
        self.task_validator.validate_task_id(task_id)

        if not self.task_validator.status_repository.status_exists(status_code):
            raise ValueError(f"Invalid CCore task status code: {status_code}")

        return self.task_repository.update_task_status(task_id, status_code)

    def delete_task(self, task_id: str) -> bool:
        self.task_validator.validate_task_id(task_id)

        return self.task_repository.delete_task(task_id)

    def execute_task(self, task_id: str) -> CCoreTaskExecution | None:
        self.task_validator.validate_task_id(task_id)
        task = self.task_repository.find_by_id(task_id)

        if task is None:
            return None

        self._validate_execution_dependencies()
        runner = self.task_runner_registry.get_runner_for_task(task)

        if runner is None:
            return self.task_execution_repository.create_execution(
                CCoreTaskExecution(
                    execution_id=None,
                    task_id=task_id,
                    status_code=CCORE_TASK_EXECUTION_STATUS_BLOCKED,
                    runner_code=None,
                    report_json={
                        "status": "BLOCKED",
                        "message": (
                            "No Automation Factory runner is registered for task: "
                            f"{task.task_name}."
                        ),
                    },
                )
            )

        runner_result = runner.execute(task)

        return self.task_execution_repository.create_execution(
            CCoreTaskExecution(
                execution_id=None,
                task_id=task_id,
                status_code=runner_result["status_code"],
                runner_code=runner_result["runner_code"],
                report_json=runner_result["report"],
            )
        )

    def get_latest_execution(self, task_id: str) -> CCoreTaskExecution | None:
        self.task_validator.validate_task_id(task_id)
        self._validate_execution_dependencies()

        return self.task_execution_repository.find_latest_by_task_id(task_id)

    def get_execution_history(self, task_id: str) -> list[CCoreTaskExecution]:
        self.task_validator.validate_task_id(task_id)
        self._validate_execution_dependencies()

        return self.task_execution_repository.find_by_task_id(task_id)

    def _validate_execution_dependencies(self) -> None:
        if self.task_execution_repository is None:
            raise ValueError("CCore task execution repository is not configured.")

        if self.task_runner_registry is None:
            raise ValueError("CCore task runner registry is not configured.")


class CCoreTaskStatusService:
    def __init__(self, status_repository: CCoreTaskStatusRepositoryProtocol):
        self.status_repository = status_repository

    def get_all_statuses(self) -> list[CCoreTaskStatus]:
        return self.status_repository.find_all_statuses()
