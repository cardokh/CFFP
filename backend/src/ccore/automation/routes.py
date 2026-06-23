from urllib.parse import unquote

from src.api.api_paths import API_PATH_CCORE_TASKS_PREFIX
from src.api.route_utils import read_json_body, send_json

from .contracts import TaskExecutionRequest, TaskExecutionResult

TASK_EXECUTION_SUFFIX_RUN = "/run"
TASK_EXECUTION_SUFFIX_EXECUTE = "/execute"

TASK_EXECUTION_INVALID_ID_MESSAGE = "Invalid CCore task id."
TASK_EXECUTION_INVALID_JSON_BODY_MESSAGE = "Invalid JSON request body."


def handle_post_ccore_task_execution_path(
    handler,
    ccore_task_service,
    path: str,
) -> None:
    if path.endswith(TASK_EXECUTION_SUFFIX_RUN):
        handle_run_ccore_task(
            handler,
            ccore_task_service,
            path,
            TASK_EXECUTION_SUFFIX_RUN,
        )
        return

    if path.endswith(TASK_EXECUTION_SUFFIX_EXECUTE):
        handle_run_ccore_task(
            handler,
            ccore_task_service,
            path,
            TASK_EXECUTION_SUFFIX_EXECUTE,
        )
        return

    _send_validation_error(handler, TASK_EXECUTION_INVALID_ID_MESSAGE)


def handle_run_ccore_task(
    handler,
    ccore_task_service,
    path: str,
    suffix: str,
) -> None:
    task_id = extract_ccore_task_id_from_suffix_path(path, suffix)
    request_data = read_json_body(handler)

    if request_data is None:
        _send_validation_error(handler, TASK_EXECUTION_INVALID_JSON_BODY_MESSAGE)
        return

    execution_request = TaskExecutionRequest(
        task_id=task_id,
        execution_provider_id=int(request_data.get("providerId", 0)),
        execution_implementer_type_id=int(request_data.get("implementerTypeId", 0)),
        execution_target_id=int(request_data.get("targetId", 0)),
        execution_configuration_id=int(request_data.get("configurationId", 0)),
        requested_by=request_data.get("requestedBy", "system"),
        input_payload=request_data.get("inputPayload", {}),
    )

    try:
        result = ccore_task_service.run_task(task_id, execution_request)

    except ValueError as error:
        _send_validation_error(handler, str(error))
        return

    except Exception as error:
        _send_server_error(handler, error)
        return

    status_code = 200

    if result.status == "FAILED":
        status_code = 500

    send_json(
        handler,
        status_code,
        {
            "success": result.status != "FAILED",
            "execution": task_execution_result_to_response(result),
        },
    )


def task_execution_result_to_response(result: TaskExecutionResult) -> dict:
    return {
        "taskId": result.task_id,
        "status": result.status,
        "message": result.message,
        "providerName": result.provider_name,
        "implementerTypeName": result.implementer_type_name,
        "targetName": result.target_name,
        "configurationName": result.configuration_name,
        "executionDetails": result.execution_details,
        "errorDetails": result.error_details,
    }


def extract_ccore_task_id_from_suffix_path(path: str, suffix: str) -> str:
    if not path.endswith(suffix):
        raise ValueError(TASK_EXECUTION_INVALID_ID_MESSAGE)

    base_path = path[: -len(suffix)]

    if not base_path.startswith(API_PATH_CCORE_TASKS_PREFIX):
        raise ValueError(TASK_EXECUTION_INVALID_ID_MESSAGE)

    task_id = unquote(base_path[len(API_PATH_CCORE_TASKS_PREFIX) :]).strip("/")

    if not task_id:
        raise ValueError(TASK_EXECUTION_INVALID_ID_MESSAGE)

    return task_id


def _send_validation_error(handler, message: str) -> None:
    send_json(
        handler,
        400,
        {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message,
            },
        },
    )


def _send_server_error(handler, error: Exception) -> None:
    send_json(
        handler,
        500,
        {
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": str(error),
            },
        },
    )
