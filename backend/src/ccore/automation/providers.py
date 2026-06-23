"""
CCore execution provider and implementer implementations.

Responsibilities:
- Provide a first metadata-driven execution path without coupling the UI to a concrete runtime technology.
- Keep the Provider as the lifecycle manager and the Implementer as the doer boundary.
- Return provider-independent execution result payloads for persistence.
"""

from .contracts import (
    ExecutionImplementer,
    ExecutionProvider,
    TaskExecutionContext,
    TaskExecutionResult,
)


class NoOpExecutionImplementer(ExecutionImplementer):
    def execute(self, context: TaskExecutionContext) -> dict:
        return {
            "summary": context.configuration_elements.get(
                "resultMessage",
                "No-op implementer completed without touching the operating system.",
            ),
            "taskId": context.task_id,
            "taskName": context.task_name,
            "providerId": context.execution_provider_id,
            "providerLabel": context.provider_label,
            "implementerTypeId": context.execution_implementer_type_id,
            "implementerTypeLabel": context.implementer_type_label,
            "targetId": context.execution_target_id,
            "targetLabel": context.target_label,
            "targetReference": context.target_reference,
            "configurationId": context.execution_configuration_id,
            "configurationLabel": context.configuration_label,
            "configurationElements": context.configuration_elements,
        }


class LocalExecutionProvider(ExecutionProvider):
    def run(
        self,
        context: TaskExecutionContext,
        implementer: ExecutionImplementer,
    ) -> TaskExecutionResult:
        try:
            outcome = implementer.execute(context)
            return TaskExecutionResult(
                task_id=context.task_id,
                status="COMPLETED",
                message="Task execution completed successfully.",
                provider_name=context.provider_label,
                implementer_type_name=context.implementer_type_label,
                target_name=context.target_label,
                configuration_name=context.configuration_label,
                execution_details={
                    "outcome": outcome,
                },
            )
        except Exception as exc:
            return TaskExecutionResult(
                task_id=context.task_id,
                status="FAILED",
                message=f"Task execution failed: {str(exc)}",
                provider_name=context.provider_label,
                implementer_type_name=context.implementer_type_label,
                target_name=context.target_label,
                configuration_name=context.configuration_label,
                error_details={
                    "exception": type(exc).__name__,
                    "message": str(exc),
                },
            )
