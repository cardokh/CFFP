"""
CCore task execution orchestration service.

Responsibilities:
- Load the automation task definition.
- Validate selected execution provider and implementer metadata.
- Create and update execution records.
- Build provider-independent execution contexts.
- Invoke the configured provider and implementer boundary.
- Persist execution lifecycle state transitions, snapshots, reports, and errors.
"""

from typing import Optional

from backend.src.ccore.tasks.task_execution import CCoreTaskExecution
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_DEFAULT_IMPLEMENTER_ID,
    CCORE_TASK_EXECUTION_DEFAULT_PROVIDER_ID,
    CCORE_TASK_EXECUTION_DEFAULT_REQUESTED_BY,
    CCORE_TASK_EXECUTION_STATUS_ID_BLOCKED,
    CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED,
    CCORE_TASK_EXECUTION_STATUS_ID_FAILED,
    CCORE_TASK_EXECUTION_STATUS_ID_PENDING,
    CCORE_TASK_EXECUTION_STATUS_ID_RUNNING,
    CCORE_TASK_EXECUTION_STATUS_LABEL_BLOCKED,
    CCORE_TASK_EXECUTION_STATUS_LABEL_COMPLETED,
    CCORE_TASK_EXECUTION_STATUS_LABEL_FAILED,
)
from backend.src.ccore.tasks.task_execution_repository_contract import (
    CCoreTaskExecutionRepositoryProtocol,
)

from .contracts import (
    ExecutionImplementer,
    ExecutionProvider,
    TaskExecutionContext,
    TaskExecutionRequest,
    TaskExecutionResult,
)
from .providers import LocalExecutionProvider, NoOpExecutionImplementer

DEFAULT_TASK_TYPE = "generic"
LOCAL_PROVIDER_ID = 1
NO_OP_IMPLEMENTER_ID = 1


class TaskExecutionService:
    def __init__(
        self,
        ccore_task_service,
        execution_provider: Optional[ExecutionProvider] = None,
        execution_implementer: Optional[ExecutionImplementer] = None,
        task_execution_repository: Optional[CCoreTaskExecutionRepositoryProtocol] = None,
    ):
        self.ccore_task_service = ccore_task_service
        self.execution_provider = execution_provider or LocalExecutionProvider()
        self.execution_implementer = execution_implementer or NoOpExecutionImplementer()
        self.task_execution_repository = task_execution_repository or getattr(
            ccore_task_service,
            "task_execution_repository",
            None,
        )

    def get_execution_providers(self):
        self._validate_execution_repository_configured()
        return self.task_execution_repository.find_all_execution_providers()

    def get_execution_implementers(self):
        self._validate_execution_repository_configured()
        return self.task_execution_repository.find_all_execution_implementers()

    def run_task(self, task_id: str, request: TaskExecutionRequest) -> TaskExecutionResult:
        self._validate_execution_repository_configured()
        task = self.ccore_task_service.get_task_by_id(task_id)

        if task is None:
            raise ValueError(f"Automation task context '{task_id}' not found.")

        provider = self._get_required_provider(request.execution_provider_id)
        implementer = self._get_required_implementer(request.execution_implementer_id)

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
                provider=provider,
                implementer=implementer,
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

            snapshot_execution = self.task_execution_repository.update_execution_snapshots(
                execution_id=str(execution.execution_id),
                configuration_snapshot=configuration_snapshot,
                validation_snapshot=validation_snapshot,
            )

            if snapshot_execution is None:
                raise RuntimeError(
                    "CCore task execution snapshots could not be persisted: "
                    f"{execution.execution_id}"
                )

            result = self._run_selected_runtime(context)
            final_status_id = self._map_result_status_to_execution_status_id(result.status)
            execution_report = self._build_execution_report(execution=execution, result=result)

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

            return self._with_execution_id(result=result, execution_id=str(execution.execution_id))

        except Exception as exc:
            error_result = self._build_failed_result(
                task_id=task_id,
                execution_id=str(execution.execution_id),
                exc=exc,
            )
            self.task_execution_repository.update_execution_result(
                execution_id=str(execution.execution_id),
                execution_status_id=CCORE_TASK_EXECUTION_STATUS_ID_FAILED,
                execution_report=self._build_execution_report(execution=execution, result=error_result),
                error_details=error_result.error_details,
            )
            return error_result

    def _validate_execution_repository_configured(self) -> None:
        if self.task_execution_repository is None:
            raise ValueError("CCore task execution repository is not configured.")

    def _get_required_provider(self, execution_provider_id: int):
        provider = self.task_execution_repository.find_execution_provider_by_id(
            execution_provider_id
        )
        if provider is None:
            raise ValueError(f"Invalid execution provider id: {execution_provider_id}")
        return provider

    def _get_required_implementer(self, execution_implementer_id: int):
        implementer = self.task_execution_repository.find_execution_implementer_by_id(
            execution_implementer_id
        )
        if implementer is None:
            raise ValueError(f"Invalid execution implementer id: {execution_implementer_id}")
        return implementer

    def _create_pending_execution(self, task_id: str, request: TaskExecutionRequest) -> CCoreTaskExecution:
        execution = CCoreTaskExecution(
            execution_id=None,
            task_id=task_id,
            execution_status_id=CCORE_TASK_EXECUTION_STATUS_ID_PENDING,
            execution_provider_id=request.execution_provider_id,
            execution_implementer_id=request.execution_implementer_id,
            requested_by=request.requested_by or CCORE_TASK_EXECUTION_DEFAULT_REQUESTED_BY,
            input_payload=request.input_payload,
            configuration_snapshot={},
            validation_snapshot={},
            execution_report={},
            error_details=None,
        )
        return self.task_execution_repository.create_execution(execution)

    def _build_execution_context(self, task, request: TaskExecutionRequest, provider, implementer) -> TaskExecutionContext:
        return TaskExecutionContext(
            task_id=str(task.task_id),
            task_name=task.task_name,
            task_type=DEFAULT_TASK_TYPE,
            execution_provider_id=provider.execution_provider_id,
            provider_label=provider.provider_label,
            execution_implementer_id=implementer.execution_implementer_id,
            implementer_label=implementer.implementer_label,
            task_metadata={},
            input_payload=request.input_payload,
            requested_by=request.requested_by,
        )

    def _run_selected_runtime(self, context: TaskExecutionContext) -> TaskExecutionResult:
        if context.execution_provider_id != LOCAL_PROVIDER_ID:
            return self._build_blocked_result(
                context=context,
                message=(
                    "The selected execution provider is registered as metadata, "
                    "but no runtime adapter is configured for this provider yet."
                ),
            )

        if context.execution_implementer_id != NO_OP_IMPLEMENTER_ID:
            return self._build_blocked_result(
                context=context,
                message=(
                    "The selected execution implementer is registered as metadata, "
                    "but no low-level implementer adapter is configured for it yet."
                ),
            )

        return self.execution_provider.run(context, self.execution_implementer)

    def _build_configuration_snapshot(self, task, request: TaskExecutionRequest, context: TaskExecutionContext) -> dict:
        return {
            "task": {
                "taskId": str(task.task_id),
                "taskName": task.task_name,
                "taskType": context.task_type,
            },
            "runtime": {
                "providerId": context.execution_provider_id,
                "providerLabel": context.provider_label,
                "implementerId": context.execution_implementer_id,
                "implementerLabel": context.implementer_label,
            },
            "request": {
                "requestedBy": request.requested_by,
            },
        }

    def _build_validation_snapshot(self, task, request: TaskExecutionRequest, context: TaskExecutionContext) -> dict:
        return {
            "status": "PASSED",
            "checks": [
                {"code": "TASK_EXISTS", "passed": task is not None, "message": "Automation task definition was found."},
                {"code": "EXECUTION_PROVIDER_SELECTED", "passed": context.execution_provider_id > 0, "message": "Execution provider was selected."},
                {"code": "EXECUTION_IMPLEMENTER_SELECTED", "passed": context.execution_implementer_id > 0, "message": "Execution implementer was selected."},
                {"code": "EXECUTION_CONTEXT_CREATED", "passed": context is not None, "message": "Execution context was created."},
                {"code": "INPUT_PAYLOAD_AVAILABLE", "passed": request.input_payload is not None, "message": "Execution input payload is available."},
            ],
        }

    def _map_result_status_to_execution_status_id(self, status: str | None) -> int:
        if status == CCORE_TASK_EXECUTION_STATUS_LABEL_FAILED:
            return CCORE_TASK_EXECUTION_STATUS_ID_FAILED
        if status == CCORE_TASK_EXECUTION_STATUS_LABEL_BLOCKED:
            return CCORE_TASK_EXECUTION_STATUS_ID_BLOCKED
        if status == CCORE_TASK_EXECUTION_STATUS_LABEL_COMPLETED or status is None:
            return CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED
        return CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED

    def _build_execution_report(self, execution: CCoreTaskExecution, result: TaskExecutionResult) -> dict:
        return {
            "executionId": str(execution.execution_id),
            "taskId": result.task_id,
            "status": result.status,
            "message": result.message,
            "providerName": result.provider_name,
            "implementerName": result.implementer_name,
            "executionDetails": result.execution_details or {},
            "errorDetails": result.error_details,
        }

    def _build_blocked_result(self, context: TaskExecutionContext, message: str) -> TaskExecutionResult:
        return TaskExecutionResult(
            task_id=context.task_id,
            status=CCORE_TASK_EXECUTION_STATUS_LABEL_BLOCKED,
            message=message,
            provider_name=context.provider_label,
            implementer_name=context.implementer_label,
            execution_details={
                "providerId": context.execution_provider_id,
                "implementerId": context.execution_implementer_id,
            },
        )

    def _build_failed_result(self, task_id: str, execution_id: str, exc: Exception) -> TaskExecutionResult:
        return TaskExecutionResult(
            task_id=task_id,
            status=CCORE_TASK_EXECUTION_STATUS_LABEL_FAILED,
            message=str(exc),
            provider_name="TaskExecutionService",
            implementer_name="TaskExecutionService",
            execution_details={"executionId": execution_id},
            error_details={"exception": type(exc).__name__, "message": str(exc)},
        )

    def _with_execution_id(self, result: TaskExecutionResult, execution_id: str) -> TaskExecutionResult:
        execution_details = dict(result.execution_details or {})
        execution_details["executionId"] = execution_id
        return TaskExecutionResult(
            task_id=result.task_id,
            status=result.status,
            message=result.message,
            provider_name=result.provider_name,
            implementer_name=result.implementer_name,
            execution_details=execution_details,
            error_details=result.error_details,
        )
