"""
CCore task execution orchestration service.

Responsibilities:
- Load the automation task definition.
- Validate selected execution provider, implementer type, target, and configuration metadata.
- Create and update execution records.
- Build provider-independent execution contexts.
- Invoke the configured provider and implementer boundary.
- Persist execution lifecycle state transitions, snapshots, reports, and errors.
"""

from typing import Optional

from backend.src.ccore.tasks.task_execution import CCoreTaskExecution
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_DEFAULT_CONFIGURATION_ID,
    CCORE_TASK_EXECUTION_DEFAULT_IMPLEMENTER_TYPE_ID,
    CCORE_TASK_EXECUTION_DEFAULT_PROVIDER_ID,
    CCORE_TASK_EXECUTION_PYTHON_SCRIPT_IMPLEMENTER_TYPE_ID,
    CCORE_TASK_EXECUTION_DEFAULT_REQUESTED_BY,
    CCORE_TASK_EXECUTION_DEFAULT_TARGET_ID,
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
from .providers import (
    LocalExecutionProvider,
    NoOpExecutionImplementer,
    PythonScriptExecutionImplementer,
)

DEFAULT_TASK_TYPE = "generic"
LOCAL_PROVIDER_ID = CCORE_TASK_EXECUTION_DEFAULT_PROVIDER_ID
NO_OP_IMPLEMENTER_TYPE_ID = CCORE_TASK_EXECUTION_DEFAULT_IMPLEMENTER_TYPE_ID
NO_OP_TARGET_ID = CCORE_TASK_EXECUTION_DEFAULT_TARGET_ID
NO_OP_CONFIGURATION_ID = CCORE_TASK_EXECUTION_DEFAULT_CONFIGURATION_ID


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
        self.python_script_execution_implementer = PythonScriptExecutionImplementer()
        self.task_execution_repository = task_execution_repository or getattr(
            ccore_task_service,
            "task_execution_repository",
            None,
        )

    def get_execution_providers(self):
        self._validate_execution_repository_configured()
        return self.task_execution_repository.find_all_execution_providers()

    def get_execution_implementer_types(self):
        self._validate_execution_repository_configured()
        return self.task_execution_repository.find_all_execution_implementer_types()

    def get_execution_targets(self):
        self._validate_execution_repository_configured()
        return self.task_execution_repository.find_all_execution_targets()

    def get_execution_configurations(self):
        self._validate_execution_repository_configured()
        return self.task_execution_repository.find_all_execution_configurations()

    def run_task(self, task_id: str, request: TaskExecutionRequest) -> TaskExecutionResult:
        self._validate_execution_repository_configured()
        task = self.ccore_task_service.get_task_by_id(task_id)

        if task is None:
            raise ValueError(f"Automation task context '{task_id}' not found.")

        provider = self._get_required_provider(request.execution_provider_id)
        implementer_type = self._get_required_implementer_type(request.execution_implementer_type_id)
        target = self._get_required_target(request.execution_target_id)
        configuration = self._get_required_configuration(request.execution_configuration_id)
        configuration_elements = self._get_configuration_elements(request.execution_configuration_id)

        self._validate_runtime_metadata_consistency(
            implementer_type=implementer_type,
            target=target,
            configuration=configuration,
        )

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
                implementer_type=implementer_type,
                target=target,
                configuration=configuration,
                configuration_elements=configuration_elements,
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

    def _get_required_implementer_type(self, execution_implementer_type_id: int):
        implementer_type = self.task_execution_repository.find_execution_implementer_type_by_id(
            execution_implementer_type_id
        )
        if implementer_type is None:
            raise ValueError(f"Invalid execution implementer type id: {execution_implementer_type_id}")
        return implementer_type

    def _get_required_target(self, execution_target_id: int):
        target = self.task_execution_repository.find_execution_target_by_id(execution_target_id)
        if target is None:
            raise ValueError(f"Invalid execution target id: {execution_target_id}")
        return target

    def _get_required_configuration(self, execution_configuration_id: int):
        configuration = self.task_execution_repository.find_execution_configuration_by_id(
            execution_configuration_id
        )
        if configuration is None:
            raise ValueError(f"Invalid execution configuration id: {execution_configuration_id}")
        return configuration

    def _get_configuration_elements(self, execution_configuration_id: int) -> dict[str, str]:
        elements = self.task_execution_repository.find_execution_configuration_elements_by_configuration_id(
            execution_configuration_id
        )
        return {element.element_name: element.element_value for element in elements}

    def _validate_runtime_metadata_consistency(self, implementer_type, target, configuration) -> None:
        if target.execution_implementer_type_id != implementer_type.execution_implementer_type_id:
            raise ValueError("Execution target does not belong to the selected implementer type.")
        if configuration.execution_target_id != target.execution_target_id:
            raise ValueError("Execution configuration does not belong to the selected target.")

    def _create_pending_execution(self, task_id: str, request: TaskExecutionRequest) -> CCoreTaskExecution:
        execution = CCoreTaskExecution(
            execution_id=None,
            task_id=task_id,
            execution_status_id=CCORE_TASK_EXECUTION_STATUS_ID_PENDING,
            execution_provider_id=request.execution_provider_id,
            execution_implementer_type_id=request.execution_implementer_type_id,
            execution_target_id=request.execution_target_id,
            execution_configuration_id=request.execution_configuration_id,
            requested_by=request.requested_by or CCORE_TASK_EXECUTION_DEFAULT_REQUESTED_BY,
            input_payload=request.input_payload,
            configuration_snapshot={},
            validation_snapshot={},
            execution_report={},
            error_details=None,
        )
        return self.task_execution_repository.create_execution(execution)

    def _build_execution_context(self, task, request: TaskExecutionRequest, provider, implementer_type, target, configuration, configuration_elements: dict[str, str]) -> TaskExecutionContext:
        return TaskExecutionContext(
            task_id=str(task.task_id),
            task_name=task.task_name,
            task_type=DEFAULT_TASK_TYPE,
            execution_provider_id=provider.execution_provider_id,
            provider_label=provider.provider_label,
            execution_implementer_type_id=implementer_type.execution_implementer_type_id,
            implementer_type_label=implementer_type.implementer_type_label,
            execution_target_id=target.execution_target_id,
            target_label=target.target_label,
            target_reference=target.target_reference,
            execution_configuration_id=configuration.execution_configuration_id,
            configuration_label=configuration.configuration_label,
            configuration_description=configuration.configuration_description,
            configuration_elements=configuration_elements,
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

        selected_implementer = self._resolve_execution_implementer(context)
        if selected_implementer is None:
            return self._build_blocked_result(
                context=context,
                message=(
                    "The selected execution implementer type is registered as metadata, "
                    "but no low-level implementer adapter is configured for it yet."
                ),
            )

        return self.execution_provider.run(context, selected_implementer)

    def _resolve_execution_implementer(self, context: TaskExecutionContext) -> ExecutionImplementer | None:
        if context.execution_implementer_type_id == NO_OP_IMPLEMENTER_TYPE_ID:
            if context.execution_target_id != NO_OP_TARGET_ID or context.execution_configuration_id != NO_OP_CONFIGURATION_ID:
                return None
            return self.execution_implementer

        if context.execution_implementer_type_id == CCORE_TASK_EXECUTION_PYTHON_SCRIPT_IMPLEMENTER_TYPE_ID:
            return self.python_script_execution_implementer

        return None

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
                "implementerTypeId": context.execution_implementer_type_id,
                "implementerTypeLabel": context.implementer_type_label,
                "targetId": context.execution_target_id,
                "targetLabel": context.target_label,
                "targetReference": context.target_reference,
                "configurationId": context.execution_configuration_id,
                "configurationLabel": context.configuration_label,
                "configurationDescription": context.configuration_description,
                "configurationElements": context.configuration_elements,
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
                {"code": "EXECUTION_IMPLEMENTER_TYPE_SELECTED", "passed": context.execution_implementer_type_id > 0, "message": "Execution implementer type was selected."},
                {"code": "EXECUTION_TARGET_SELECTED", "passed": context.execution_target_id > 0, "message": "Execution target was selected."},
                {"code": "EXECUTION_CONFIGURATION_SELECTED", "passed": context.execution_configuration_id > 0, "message": "Execution configuration was selected."},
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
            "implementerTypeName": result.implementer_type_name,
            "targetName": result.target_name,
            "configurationName": result.configuration_name,
            "executionDetails": result.execution_details or {},
            "errorDetails": result.error_details,
        }

    def _build_blocked_result(self, context: TaskExecutionContext, message: str) -> TaskExecutionResult:
        return TaskExecutionResult(
            task_id=context.task_id,
            status=CCORE_TASK_EXECUTION_STATUS_LABEL_BLOCKED,
            message=message,
            provider_name=context.provider_label,
            implementer_type_name=context.implementer_type_label,
            target_name=context.target_label,
            configuration_name=context.configuration_label,
            execution_details={
                "providerId": context.execution_provider_id,
                "implementerTypeId": context.execution_implementer_type_id,
                "targetId": context.execution_target_id,
                "configurationId": context.execution_configuration_id,
            },
        )

    def _build_failed_result(self, task_id: str, execution_id: str, exc: Exception) -> TaskExecutionResult:
        return TaskExecutionResult(
            task_id=task_id,
            status=CCORE_TASK_EXECUTION_STATUS_LABEL_FAILED,
            message=str(exc),
            provider_name="TaskExecutionService",
            implementer_type_name="TaskExecutionService",
            target_name="TaskExecutionService",
            configuration_name="TaskExecutionService",
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
            implementer_type_name=result.implementer_type_name,
            target_name=result.target_name,
            configuration_name=result.configuration_name,
            execution_details=execution_details,
            error_details=result.error_details,
        )
