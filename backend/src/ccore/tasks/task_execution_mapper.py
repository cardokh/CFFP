"""
CCore task execution mapper.

Responsibilities:
- Convert task execution domain objects to API response dictionaries.
- Convert execution runtime lookup metadata to the shared { id, label } API shape.
- Keep execution API field names camelCase while preserving database/domain names internally.
"""

from backend.src.ccore.tasks.task_execution import (
    CCoreExecutionConfiguration,
    CCoreExecutionConfigurationElement,
    CCoreExecutionImplementerType,
    CCoreExecutionProvider,
    CCoreExecutionTarget,
    CCoreTaskExecution,
)
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_API_FIELD_COMPLETED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_DESCRIPTION,
    CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_ID,
    CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_LABEL,
    CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_SNAPSHOT,
    CCORE_TASK_EXECUTION_API_FIELD_CREATED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_ERROR_DETAILS,
    CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_ID,
    CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_REPORT,
    CCORE_TASK_EXECUTION_API_FIELD_FAILED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_IMPLEMENTER_TYPE_ID,
    CCORE_TASK_EXECUTION_API_FIELD_IMPLEMENTER_TYPE_LABEL,
    CCORE_TASK_EXECUTION_API_FIELD_INPUT_PAYLOAD,
    CCORE_TASK_EXECUTION_API_FIELD_PROVIDER_ID,
    CCORE_TASK_EXECUTION_API_FIELD_PROVIDER_LABEL,
    CCORE_TASK_EXECUTION_API_FIELD_REQUESTED_BY,
    CCORE_TASK_EXECUTION_API_FIELD_STARTED_AT,
    CCORE_TASK_EXECUTION_API_FIELD_STATUS,
    CCORE_TASK_EXECUTION_API_FIELD_STATUS_ID,
    CCORE_TASK_EXECUTION_API_FIELD_STATUS_LABEL,
    CCORE_TASK_EXECUTION_API_FIELD_TARGET_ID,
    CCORE_TASK_EXECUTION_API_FIELD_TARGET_LABEL,
    CCORE_TASK_EXECUTION_API_FIELD_TARGET_REFERENCE,
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
            CCORE_TASK_EXECUTION_API_FIELD_PROVIDER_ID: execution.execution_provider_id,
            CCORE_TASK_EXECUTION_API_FIELD_PROVIDER_LABEL: execution.provider_label,
            CCORE_TASK_EXECUTION_API_FIELD_IMPLEMENTER_TYPE_ID: execution.execution_implementer_type_id,
            CCORE_TASK_EXECUTION_API_FIELD_IMPLEMENTER_TYPE_LABEL: execution.implementer_type_label,
            CCORE_TASK_EXECUTION_API_FIELD_TARGET_ID: execution.execution_target_id,
            CCORE_TASK_EXECUTION_API_FIELD_TARGET_LABEL: execution.target_label,
            CCORE_TASK_EXECUTION_API_FIELD_TARGET_REFERENCE: execution.target_reference,
            CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_ID: execution.execution_configuration_id,
            CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_LABEL: execution.configuration_label,
            CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_DESCRIPTION: execution.configuration_description,
            CCORE_TASK_EXECUTION_API_FIELD_REQUESTED_BY: execution.requested_by,
            CCORE_TASK_EXECUTION_API_FIELD_INPUT_PAYLOAD: execution.input_payload or {},
            CCORE_TASK_EXECUTION_API_FIELD_CONFIGURATION_SNAPSHOT: execution.configuration_snapshot or {},
            CCORE_TASK_EXECUTION_API_FIELD_VALIDATION_SNAPSHOT: execution.validation_snapshot or {},
            CCORE_TASK_EXECUTION_API_FIELD_EXECUTION_REPORT: execution.execution_report or {},
            CCORE_TASK_EXECUTION_API_FIELD_ERROR_DETAILS: execution.error_details,
            CCORE_TASK_EXECUTION_API_FIELD_STARTED_AT: execution.started_at,
            CCORE_TASK_EXECUTION_API_FIELD_COMPLETED_AT: execution.completed_at,
            CCORE_TASK_EXECUTION_API_FIELD_FAILED_AT: execution.failed_at,
            CCORE_TASK_EXECUTION_API_FIELD_CREATED_AT: execution.created_at,
            CCORE_TASK_EXECUTION_API_FIELD_UPDATED_AT: execution.updated_at,
        }

    def domains_to_response(self, executions: list[CCoreTaskExecution]) -> list[dict]:
        return [self.domain_to_response(execution) for execution in executions]

    def provider_to_response(self, provider: CCoreExecutionProvider) -> dict:
        return {
            "id": provider.execution_provider_id,
            "label": provider.provider_label,
        }

    def providers_to_response(self, providers: list[CCoreExecutionProvider]) -> list[dict]:
        return [self.provider_to_response(provider) for provider in providers]

    def implementer_type_to_response(self, implementer_type: CCoreExecutionImplementerType) -> dict:
        return {
            "id": implementer_type.execution_implementer_type_id,
            "label": implementer_type.implementer_type_label,
        }

    def implementer_types_to_response(self, implementer_types: list[CCoreExecutionImplementerType]) -> list[dict]:
        return [self.implementer_type_to_response(implementer_type) for implementer_type in implementer_types]

    def target_to_response(self, target: CCoreExecutionTarget) -> dict:
        return {
            "id": target.execution_target_id,
            "label": target.target_label,
            "implementerTypeId": target.execution_implementer_type_id,
            "targetReference": target.target_reference,
        }

    def targets_to_response(self, targets: list[CCoreExecutionTarget]) -> list[dict]:
        return [self.target_to_response(target) for target in targets]

    def configuration_to_response(self, configuration: CCoreExecutionConfiguration) -> dict:
        return {
            "id": configuration.execution_configuration_id,
            "label": configuration.configuration_label,
            "targetId": configuration.execution_target_id,
            "description": configuration.configuration_description,
        }

    def configurations_to_response(self, configurations: list[CCoreExecutionConfiguration]) -> list[dict]:
        return [self.configuration_to_response(configuration) for configuration in configurations]

    def configuration_element_to_response(self, element: CCoreExecutionConfigurationElement) -> dict:
        return {
            "id": element.execution_configuration_element_id,
            "configurationId": element.execution_configuration_id,
            "name": element.element_name,
            "value": element.element_value,
            "sortOrder": element.sort_order,
        }

    def configuration_elements_to_response(self, elements: list[CCoreExecutionConfigurationElement]) -> list[dict]:
        return [self.configuration_element_to_response(element) for element in elements]
