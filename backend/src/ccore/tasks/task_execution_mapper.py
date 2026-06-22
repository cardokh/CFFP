"""
CCore task execution mapper.

Responsibilities:
- Convert task execution domain objects to API response dictionaries.
- Keep execution API field names camelCase while preserving database/domain names internally.
"""

from backend.src.ccore.tasks.task_execution import CCoreTaskExecution
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_API_FIELD_CREATED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_ID,
    CCORE_TASK_EXECUTION_API_FIELD_FINISHED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_REPORT,
    CCORE_TASK_EXECUTION_API_FIELD_RUNNER_CODE,
    CCORE_TASK_EXECUTION_API_FIELD_STARTED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_STATUS,
    CCORE_TASK_EXECUTION_API_FIELD_STATUS_LABEL,
    CCORE_TASK_EXECUTION_API_FIELD_TASK_ID,
)


class CCoreTaskExecutionMapper:
    def domain_to_response(self, execution: CCoreTaskExecution) -> dict:
        return {
            CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_ID: execution.execution_id,
            CCORE_TASK_EXECUTION_API_FIELD_TASK_ID: execution.task_id,
            CCORE_TASK_EXECUTION_API_FIELD_STATUS: execution.status_code,
            CCORE_TASK_EXECUTION_API_FIELD_STATUS_LABEL: execution.status_label,
            CCORE_TASK_EXECUTION_API_FIELD_RUNNER_CODE: execution.runner_code,
            CCORE_TASK_EXECUTION_API_FIELD_REPORT: execution.report_json or {},
            CCORE_TASK_EXECUTION_API_FIELD_STARTED_AT: execution.started_at,
            CCORE_TASK_EXECUTION_API_FIELD_FINISHED_AT: execution.finished_at,
            CCORE_TASK_EXECUTION_API_FIELD_CREATED_AT: execution.created_at,
        }

    def domains_to_response(self, executions: list[CCoreTaskExecution]) -> list[dict]:
        return [self.domain_to_response(execution) for execution in executions]
