"""
CCore task execution mapper.

Responsibilities:
- Convert task execution domain objects to API response dictionaries.
- Keep execution API field names camelCase while preserving database/domain names internally.
"""

from backend.src.ccore.tasks.task_execution import CCoreTaskExecution
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_API_FIELD_COMPLETED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_SNAPSHOT,
    CCORE_TASK_EXECUTION_API_FIELD_CREATED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_ERROR_DETAILS,
    CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_ID,
    CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_MODE,
    CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_REPORT,
    CCORE_TASK_EXECUTION_API_FIELD_FAILED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_INPUT_PAYLOAD,
    CCORE_TASK_EXECUTION_API_FIELD_PROVIDER_PROFILE,
    CCORE_TASK_EXECUTION_API_FIELD_REQUESTED_BY,
    CCORE_TASK_EXECUTION_API_FIELD_STARTED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_STATUS,
    CCORE_TASK_EXECUTION_API_FIELD_STATUS_ID,
    CCORE_TASK_EXECUTION_API_FIELD_STATUS_LABEL,
    CCORE_TASK_EXECUTION_API_FIELD_TASK_ID,
    CCORE_TASK_EXECUTION_API_FIELD_UPDATED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_VALIDATION_SNAPSHOT,
)


class CCoreTaskExecutionMapper:
    def domain_to_response(self, execution: CCoreTaskExecution) -> dict:
        return {
            CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_ID: execution.execution_id,
            CCORE_TASK_EXECUTION_API_FIELD_TASK_ID: execution.task_id,
            CCORE_TASK_EXECUTION_API_FIELD_STATUS: execution.status_label,
            CCORE_TASK_EXECUTION_API_FIELD_STATUS_ID: execution.execution_status_id,
            CCORE_TASK_EXECUTION_API_FIELD_STATUS_LABEL: execution.status_label,
            CCORE_TASK_EXECUTION_API_FIELD_PROVIDER_PROFILE: execution.provider_profile,
            CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_MODE: execution.execution_mode,
            CCORE_TASK_EXECUTION_API_FIELD_REQUESTED_BY: execution.requested_by,
            CCORE_TASK_EXECUTION_API_FIELD_INPUT_PAYLOAD: execution.input_payload or {},
            CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_SNAPSHOT: execution.configuration_snapshot
            or {},
            CCORE_TASK_EXECUTION_API_FIELD_VALIDATION_SNAPSHOT: execution.validation_snapshot
            or {},
            CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_REPORT: execution.execution_report
            or {},
            CCORE_TASK_EXECUTION_API_FIELD_ERROR_DETAILS: execution.error_details,
            CCORE_TASK_EXECUTION_API_FIELD_STARTED_AT: execution.started_at,
            CCORE_TASK_EXECUTION_API_FIELD_COMPLETED_AT: execution.completed_at,
            CCORE_TASK_EXECUTION_API_FIELD_FAILED_AT: execution.failed_at,
            CCORE_TASK_EXECUTION_API_FIELD_CREATED_AT: execution.created_at,
            CCORE_TASK_EXECUTION_API_FIELD_UPDATED_AT: execution.updated_at,
        }

    def domains_to_response(
        self,
        executions: list[CCoreTaskExecution],
    ) -> list[dict]:
        return [self.domain_to_response(execution) for execution in executions]
