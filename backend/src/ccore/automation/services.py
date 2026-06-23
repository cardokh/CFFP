from typing import Optional

from .contracts import (
    ExecutionProvider,
    TaskExecutionContext,
    TaskExecutionRequest,
    TaskExecutionResult,
)
from .providers import PrefectExecutionProvider

TASK_STATUS_RUNNING = "RUNNING"
TASK_STATUS_COMPLETED = "COMPLETED"
TASK_STATUS_FAILED = "FAILED"

DEFAULT_TASK_TYPE = "generic"
DEFAULT_PROVIDER_PROFILE = "prefect"


class TaskExecutionService:
    def __init__(
        self,
        ccore_task_service,
        execution_provider: Optional[ExecutionProvider] = None,
    ):
        self.ccore_task_service = ccore_task_service
        self.execution_provider = execution_provider or PrefectExecutionProvider()

    def run_task(
        self,
        task_id: str,
        request: TaskExecutionRequest,
    ) -> TaskExecutionResult:
        task = self.ccore_task_service.get_task_by_id(task_id)

        if task is None:
            raise ValueError(f"Automation task context '{task_id}' not found.")

        try:
            self.ccore_task_service.update_task_status(task_id, TASK_STATUS_RUNNING)

            context = self._build_execution_context(
                task=task,
                request=request,
            )

            result = self.execution_provider.run(context)

            final_status = result.status or TASK_STATUS_COMPLETED
            self.ccore_task_service.update_task_status(task_id, final_status)

            return result

        except Exception as exc:
            self.ccore_task_service.update_task_status(task_id, TASK_STATUS_FAILED)

            return TaskExecutionResult(
                task_id=task_id,
                status=TASK_STATUS_FAILED,
                message=str(exc),
                provider_name="TaskExecutionService",
                error_details={
                    "exception": type(exc).__name__,
                    "message": str(exc),
                },
            )

    def _build_execution_context(
        self,
        task,
        request: TaskExecutionRequest,
    ) -> TaskExecutionContext:
        return TaskExecutionContext(
            task_id=str(task.task_id),
            task_name=task.task_name,
            task_type=DEFAULT_TASK_TYPE,
            provider_profile=DEFAULT_PROVIDER_PROFILE,
            task_metadata={},
            input_payload=request.input_payload,
            execution_mode=request.execution_mode,
        )
