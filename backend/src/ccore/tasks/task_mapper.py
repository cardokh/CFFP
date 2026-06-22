"""
CCore task mapper.

Responsibilities:
- Convert task request contracts to domain objects.
- Convert task domain objects and reference data to API response dictionaries.
- Keep API field names camelCase while preserving database/domain names internally.
"""

from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_constants import (
    CCORE_TASK_API_FIELD_CREATED_AT,
    CCORE_TASK_API_FIELD_STATUS,
    CCORE_TASK_API_FIELD_STATUS_LABEL,
    CCORE_TASK_API_FIELD_TASK_ID,
    CCORE_TASK_API_FIELD_TASK_NAME,
    CCORE_TASK_API_FIELD_UPDATED_AT,
    CCORE_TASK_DEFAULT_STATUS_CODE,
    CCORE_TASK_STATUS_API_FIELD_CODE,
    CCORE_TASK_STATUS_API_FIELD_LABEL,
    CCORE_TASK_STATUS_API_FIELD_SORT_ORDER,
)
from backend.src.ccore.tasks.task_contracts import (
    CreateCCoreTaskRequest,
    UpdateCCoreTaskRequest,
)
from backend.src.ccore.tasks.task_status import CCoreTaskStatus


class CCoreTaskMapper:
    def create_request_to_domain(
        self,
        request: CreateCCoreTaskRequest,
    ) -> CCoreTask:
        return CCoreTask(
            task_id=None,
            task_name=request.task_name,
            status_code=request.status_code or CCORE_TASK_DEFAULT_STATUS_CODE,
        )

    def update_request_to_domain(
        self,
        request: UpdateCCoreTaskRequest,
    ) -> CCoreTask:
        return CCoreTask(
            task_id=request.task_id,
            task_name=request.task_name,
            status_code=request.status_code,
        )

    def domain_to_response(self, task: CCoreTask) -> dict:
        return {
            CCORE_TASK_API_FIELD_TASK_ID: task.task_id,
            CCORE_TASK_API_FIELD_TASK_NAME: task.task_name,
            CCORE_TASK_API_FIELD_STATUS: task.status_code,
            CCORE_TASK_API_FIELD_STATUS_LABEL: task.status_label,
            CCORE_TASK_API_FIELD_CREATED_AT: task.created_at,
            CCORE_TASK_API_FIELD_UPDATED_AT: task.updated_at,
        }

    def domains_to_response(self, tasks: list[CCoreTask]) -> list[dict]:
        return [self.domain_to_response(task) for task in tasks]

    def status_to_response(self, status: CCoreTaskStatus) -> dict:
        return {
            CCORE_TASK_STATUS_API_FIELD_CODE: status.status_code,
            CCORE_TASK_STATUS_API_FIELD_LABEL: status.status_label,
            CCORE_TASK_STATUS_API_FIELD_SORT_ORDER: status.sort_order,
        }

    def statuses_to_response(self, statuses: list[CCoreTaskStatus]) -> list[dict]:
        return [self.status_to_response(status) for status in statuses]
