"""
CCore task execution orchestration service.

Responsibilities:
- Load the automation task definition.
- Create and update execution records.
- Build provider-independent execution contexts.
- Invoke the configured execution provider.
- Persist execution lifecycle state transitions.
- Persist configuration snapshots, validation snapshots, reports, and errors.
- Return the execution result.

Architectural boundaries:
- TaskExecutionService owns execution orchestration.
- CCoreTaskService owns task CRUD/business operations.
- Repositories own persistence.
- ExecutionProvider implementations own runtime execution.
"""

from typing import Optional

from backend.src.ccore.tasks.task_execution import CCoreTaskExecution
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_DEFAULT_MODE,
    CCORE_TASK_EXECUTION_DEFAULT_PROVIDER_PROFILE,
    CCORE_TASK_EXECUTION_DEFAULT_REQUESTED_BY,
    CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED,
    CCORE_TASK_EXECUTION_STATUS_ID_FAILED,
    CCORE_TASK_EXECUTION_STATUS_ID_PENDING,
    CCORE_TASK_EXECUTION_STATUS_ID_RUNNING,
    CCORE_TASK_EXECUTION_STATUS_LABEL_COMPLETED,
    CCORE_TASK_EXECUTION_STATUS_LABEL_FAILED,
)
from backend.src.ccore.tasks.task_execution_repository_contract import (
    CCoreTaskExecutionRepositoryProtocol,
)

from .contracts import (
    ExecutionProvider,
    TaskExecutionContext,
    TaskExecutionRequest,
    TaskExecutionResult,
)
from .providers import PrefectExecutionProvider

# Temporary default execution metadata.
DEFAULT_TASK_TYPE = "generic"


class TaskExecutionService:
    """
    Coordinates the execution lifecycle of an automation task.

    This service deliberately orchestrates execution records instead of updating
    the task definition itself. A task is a reusable template; an execution is
    one individual run of that task.
    """

    def __init__(
        self,
        ccore_task_service,
        execution_provider: Optional[ExecutionProvider] = None,
        task_execution_repository: Optional[
            CCoreTaskExecutionRepositoryProtocol
        ] = None,
    ):
        self.ccore_task_service = ccore_task_service
        self.execution_provider = execution_provider or PrefectExecutionProvider()
        self.task_execution_repository = task_execution_repository or getattr(
            ccore_task_service, "task_execution_repository", None
        )

    def run_task(
        self,
        task_id: str,
        request: TaskExecutionRequest,
    ) -> TaskExecutionResult:
        """
        Execute one automation task and persist its execution lifecycle.

        Lifecycle:
        - Validate and load the task definition.
        - Create a new execution record.
        - Transition the execution to RUNNING.
        - Build and persist execution snapshots.
        - Invoke the configured execution provider.
        - Persist COMPLETED or FAILED result data.
        - Return the provider-compatible execution result.
        """
        self._validate_execution_repository_configured()

        task = self.ccore_task_service.get_task_by_id(task_id)

        if task is None:
            raise ValueError(f"Automation task context '{task_id}' not found.")

        execution = self._create_pending_execution(
            task_id=task_id,
            request=request,
        )

        try:
            running_execution = self.task_execution_repository.update_execution_status(
                execution_id=str(execution.execution_id),
                execution_status_id=CCORE_TASK_EXECUTION_STATUS_ID_RUNNING,
            )

            if running_execution is None:
                raise RuntimeError(
                    "CCore task execution could not be moved to RUNNING: "
                    f"{execution.execution_id}"
                )

            context = self._build_execution_context(
                task=task,
                request=request,
            )

            configuration_snapshot = self._build_configuration_snapshot(
                task=task,
                request=request,
                context=context,
            )
            validation_snapshot = self._build_validation_snapshot(
                task=task,
                request=request,
                context=context,
            )

            snapshot_execution = (
                self.task_execution_repository.update_execution_snapshots(
                    execution_id=str(execution.execution_id),
                    configuration_snapshot=configuration_snapshot,
                    validation_snapshot=validation_snapshot,
                )
            )

            if snapshot_execution is None:
                raise RuntimeError(
                    "CCore task execution snapshots could not be persisted: "
                    f"{execution.execution_id}"
                )

            result = self.execution_provider.run(context)

            final_status_id = self._map_result_status_to_execution_status_id(result.status)
            execution_report = self._build_execution_report(
                execution=execution,
                result=result,
            )

            final_execution = self.task_execution_repository.update_execution_result(
                execution_id=str(execution.execution_id),
                execution_status_id=final_status_id,
                execution_report=execution_report,
                error_details=result.error_details,
            )

            if final_execution is None:
                raise RuntimeError(
                    "CCore task execution result could not be persisted: "
                    f"{execution.execution_id}"
                )

            return self._with_execution_id(
                result=result,
                execution_id=str(execution.execution_id),
            )

        except Exception as exc:
            error_result = self._build_failed_result(
                task_id=task_id,
                execution_id=str(execution.execution_id),
                exc=exc,
            )

            self.task_execution_repository.update_execution_result(
                execution_id=str(execution.execution_id),
                execution_status_id=CCORE_TASK_EXECUTION_STATUS_ID_FAILED,
                execution_report=self._build_execution_report(
                    execution=execution,
                    result=error_result,
                ),
                error_details=error_result.error_details,
            )

            return error_result

    def _validate_execution_repository_configured(self) -> None:
        """Ensure the execution repository dependency is available."""
        if self.task_execution_repository is None:
            raise ValueError("CCore task execution repository is not configured.")

    def _create_pending_execution(
        self,
        task_id: str,
        request: TaskExecutionRequest,
    ) -> CCoreTaskExecution:
        """Create the initial execution record before runtime execution starts."""
        execution = CCoreTaskExecution(
            execution_id=None,
            task_id=task_id,
            execution_status_id=CCORE_TASK_EXECUTION_STATUS_ID_PENDING,
            provider_profile=CCORE_TASK_EXECUTION_DEFAULT_PROVIDER_PROFILE,
            execution_mode=request.execution_mode or CCORE_TASK_EXECUTION_DEFAULT_MODE,
            requested_by=request.requested_by
            or CCORE_TASK_EXECUTION_DEFAULT_REQUESTED_BY,
            input_payload=request.input_payload,
            configuration_snapshot={},
            validation_snapshot={},
            execution_report={},
            error_details=None,
        )

        return self.task_execution_repository.create_execution(execution)

    def _build_execution_context(
        self,
        task,
        request: TaskExecutionRequest,
    ) -> TaskExecutionContext:
        """
        Build the provider-independent execution context.

        Execution providers receive this context instead of direct access to
        task services, repositories, or API request objects.
        """
        return TaskExecutionContext(
            task_id=str(task.task_id),
            task_name=task.task_name,
            task_type=DEFAULT_TASK_TYPE,
            provider_profile=CCORE_TASK_EXECUTION_DEFAULT_PROVIDER_PROFILE,
            task_metadata={},
            input_payload=request.input_payload,
            execution_mode=request.execution_mode,
        )

    def _build_configuration_snapshot(
        self,
        task,
        request: TaskExecutionRequest,
        context: TaskExecutionContext,
    ) -> dict:
        """
        Build the configuration snapshot for this execution.

        This snapshot records the execution configuration as seen by the
        orchestration layer at runtime. It is intentionally persisted against
        the execution, not the reusable task definition.
        """
        return {
            "task": {
                "taskId": str(task.task_id),
                "taskName": task.task_name,
                "taskType": context.task_type,
            },
            "provider": {
                "providerProfile": context.provider_profile,
                "providerName": self.execution_provider.__class__.__name__,
            },
            "request": {
                "executionMode": request.execution_mode,
                "requestedBy": request.requested_by,
            },
        }

    def _build_validation_snapshot(
        self,
        task,
        request: TaskExecutionRequest,
        context: TaskExecutionContext,
    ) -> dict:
        """
        Build the validation snapshot for this execution.

        This first lifecycle slice records the validations already guaranteed by
        the orchestration flow. Later slices can replace or extend this with a
        dedicated validation provider without changing the execution repository.
        """
        return {
            "status": "PASSED",
            "checks": [
                {
                    "code": "TASK_EXISTS",
                    "passed": task is not None,
                    "message": "Automation task definition was found.",
                },
                {
                    "code": "EXECUTION_PROVIDER_CONFIGURED",
                    "passed": self.execution_provider is not None,
                    "message": "Execution provider is configured.",
                },
                {
                    "code": "EXECUTION_CONTEXT_CREATED",
                    "passed": context is not None,
                    "message": "Execution context was created.",
                },
                {
                    "code": "INPUT_PAYLOAD_AVAILABLE",
                    "passed": request.input_payload is not None,
                    "message": "Execution input payload is available.",
                },
            ],
        }


    def _map_result_status_to_execution_status_id(self, status: str | None) -> int:
        """Map provider result status text into CCore execution status IDs."""
        if status == CCORE_TASK_EXECUTION_STATUS_LABEL_FAILED:
            return CCORE_TASK_EXECUTION_STATUS_ID_FAILED

        if status == CCORE_TASK_EXECUTION_STATUS_LABEL_COMPLETED or status is None:
            return CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED

        return CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED

    def _build_execution_report(
        self,
        execution: CCoreTaskExecution,
        result: TaskExecutionResult,
    ) -> dict:
        """
        Build the persisted execution report from the provider result.
        """
        return {
            "executionId": str(execution.execution_id),
            "taskId": result.task_id,
            "status": result.status,
            "message": result.message,
            "providerName": result.provider_name,
            "executionDetails": result.execution_details or {},
            "errorDetails": result.error_details,
        }

    def _build_failed_result(
        self,
        task_id: str,
        execution_id: str,
        exc: Exception,
    ) -> TaskExecutionResult:
        """Build a provider-compatible failure result for orchestration errors."""
        return TaskExecutionResult(
            task_id=task_id,
            status=CCORE_TASK_EXECUTION_STATUS_LABEL_FAILED,
            message=str(exc),
            provider_name="TaskExecutionService",
            execution_details={
                "executionId": execution_id,
            },
            error_details={
                "exception": type(exc).__name__,
                "message": str(exc),
            },
        )

    def _with_execution_id(
        self,
        result: TaskExecutionResult,
        execution_id: str,
    ) -> TaskExecutionResult:
        """
        Return the provider result enriched with the persisted execution id.

        TaskExecutionResult does not yet expose execution_id as a first-class
        field, so the identifier is added to execution_details for this slice.
        """
        execution_details = dict(result.execution_details or {})
        execution_details["executionId"] = execution_id

        return TaskExecutionResult(
            task_id=result.task_id,
            status=result.status,
            message=result.message,
            provider_name=result.provider_name,
            execution_details=execution_details,
            error_details=result.error_details,
        )
