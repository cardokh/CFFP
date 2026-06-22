"""
CCore task mapper.

Responsibilities:
- Convert task request contracts to domain objects.
- Convert task domain objects to API response dictionaries.
- Keep API field names camelCase while preserving database/domain names internally.
"""

from src.core.tasks.task import CCoreTask
from src.core.tasks.task_contracts import (
    CreateCCoreTaskRequest,
    UpdateCCoreTaskRequest,
)


class CCoreTaskMapper:
    def create_request_to_domain(
        self,
        request: CreateCCoreTaskRequest,
    ) -> CCoreTask:
        return CCoreTask(
            task_id=None,
            task_name=request.task_name,
            status=request.status or "PENDING",
        )

    def update_request_to_domain(
        self,
        request: UpdateCCoreTaskRequest,
    ) -> CCoreTask:
        return CCoreTask(
            task_id=request.task_id,
            task_name=request.task_name,
            status=request.status,
        )

    def domain_to_response(self, task: CCoreTask) -> dict:
        return {
            "id": task.task_id,
            "taskId": task.task_id,
            "name": task.task_name,
            "taskName": task.task_name,
            "status": task.status,
            "createdAt": task.created_at,
        }

    def domains_to_response(self, tasks: list[CCoreTask]) -> list[dict]:
        return [self.domain_to_response(task) for task in tasks]
