"""
CCore task API routes.

Responsibilities:
- Handle CCore task CRUD HTTP requests.
- Handle CCore task reference-data requests.
- Delegate request payload parsing to API request contracts.
- Delegate business use cases to CCoreTaskService.
- Delegate task execution requests to TaskExecutionService.
- Return consistent JSON responses.
"""

from urllib.parse import unquote

from backend.src.ccore.automation.contracts import (
    TaskExecutionRequest,
    TaskExecutionResult,
)
from backend.src.ccore.tasks.task_contracts import CCoreTaskRequestParser
from backend.src.ccore.tasks.task_execution_mapper import CCoreTaskExecutionMapper
from backend.src.ccore.tasks.task_mapper import CCoreTaskMapper
from backend.src.ccore.tasks.task_messages import (
    CCORE_TASK_CREATED_SUCCESS_MESSAGE,
    CCORE_TASK_DELETED_SUCCESS_MESSAGE,
    CCORE_TASK_ERROR_CODE_NOT_FOUND,
    CCORE_TASK_ERROR_CODE_SERVER,
    CCORE_TASK_ERROR_CODE_VALIDATION,
    CCORE_TASK_INVALID_ID_MESSAGE,
    CCORE_TASK_INVALID_JSON_BODY_MESSAGE,
    CCORE_TASK_NOT_FOUND_MESSAGE,
    CCORE_TASK_UPDATED_SUCCESS_MESSAGE,
)
from src.api.api_paths import API_PATH_CCORE_TASKS_PREFIX
from src.api.route_utils import read_json_body, send_json

CCORE_TASK_EXECUTE_SUFFIX = "/execute"

ccore_task_mapper = CCoreTaskMapper()
ccore_task_execution_mapper = CCoreTaskExecutionMapper()
ccore_task_request_parser = CCoreTaskRequestParser()


def _send_success(handler, status_code: int, payload: dict) -> None:
    send_json(handler, status_code, {"success": True, **payload})


def _send_error(handler, status_code: int, code: str, message: str) -> None:
    send_json(
        handler,
        status_code,
        {
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def _send_validation_error(handler, message: str) -> None:
    _send_error(handler, 400, CCORE_TASK_ERROR_CODE_VALIDATION, message)


def _send_not_found_error(handler) -> None:
    _send_error(
        handler,
        404,
        CCORE_TASK_ERROR_CODE_NOT_FOUND,
        CCORE_TASK_NOT_FOUND_MESSAGE,
    )


def _send_server_error(handler, error: Exception) -> None:
    _send_error(handler, 500, CCORE_TASK_ERROR_CODE_SERVER, str(error))


def handle_get_ccore_tasks(handler, ccore_task_service) -> None:
    try:
        tasks = ccore_task_service.get_all_tasks()

    except Exception as error:
        _send_server_error(handler, error)
        return

    _send_success(
        handler,
        200,
        {
            "tasks": ccore_task_mapper.domains_to_response(tasks),
        },
    )


def handle_get_ccore_task_statuses(handler, ccore_task_status_service) -> None:
    try:
        statuses = ccore_task_status_service.get_all_statuses()

    except Exception as error:
        _send_server_error(handler, error)
        return

    _send_success(
        handler,
        200,
        {
            "statuses": ccore_task_mapper.statuses_to_response(statuses),
        },
    )


def handle_get_ccore_execution_providers(handler, task_execution_service) -> None:
    try:
        providers = task_execution_service.get_execution_providers()

    except Exception as error:
        _send_server_error(handler, error)
        return

    _send_success(
        handler,
        200,
        {
            "providers": ccore_task_execution_mapper.providers_to_response(providers),
        },
    )


def handle_get_ccore_execution_implementers(handler, task_execution_service) -> None:
    try:
        implementers = task_execution_service.get_execution_implementers()

    except Exception as error:
        _send_server_error(handler, error)
        return

    _send_success(
        handler,
        200,
        {
            "implementers": ccore_task_execution_mapper.implementers_to_response(implementers),
        },
    )


def handle_get_ccore_task_path(handler, ccore_task_service, path: str) -> None:
    if path.endswith("/executions"):
        handle_get_ccore_task_executions(handler, ccore_task_service, path)
        return

    handle_get_ccore_task_by_id(handler, ccore_task_service, path)


def handle_post_ccore_task_path(handler, task_execution_service, path: str) -> None:
    if path.endswith(CCORE_TASK_EXECUTE_SUFFIX):
        handle_execute_ccore_task_path(handler, task_execution_service, path)
        return

    _send_validation_error(handler, CCORE_TASK_INVALID_ID_MESSAGE)


def handle_get_ccore_task_by_id(handler, ccore_task_service, path: str) -> None:
    task_id = extract_ccore_task_id(path)

    try:
        task = ccore_task_service.get_task_by_id(task_id)

    except ValueError as error:
        _send_validation_error(handler, str(error))
        return

    except Exception as error:
        _send_server_error(handler, error)
        return

    if task is None:
        _send_not_found_error(handler)
        return

    _send_success(
        handler,
        200,
        {
            "task": ccore_task_mapper.domain_to_response(task),
        },
    )


def handle_create_ccore_task(handler, ccore_task_service) -> None:
    request_data = read_json_body(handler)

    if request_data is None:
        _send_validation_error(handler, CCORE_TASK_INVALID_JSON_BODY_MESSAGE)
        return

    try:
        create_request = ccore_task_request_parser.parse_create_request(request_data)
        task = ccore_task_mapper.create_request_to_domain(create_request)
        created_task = ccore_task_service.create_task(task)

    except ValueError as error:
        _send_validation_error(handler, str(error))
        return

    except Exception as error:
        _send_server_error(handler, error)
        return

    _send_success(
        handler,
        201,
        {
            "message": CCORE_TASK_CREATED_SUCCESS_MESSAGE,
            "task": ccore_task_mapper.domain_to_response(created_task),
        },
    )


def handle_update_ccore_task(handler, ccore_task_service, path: str) -> None:
    task_id = extract_ccore_task_id(path)
    request_data = read_json_body(handler)

    if request_data is None:
        _send_validation_error(handler, CCORE_TASK_INVALID_JSON_BODY_MESSAGE)
        return

    try:
        update_request = ccore_task_request_parser.parse_update_request(
            task_id,
            request_data,
        )
        task = ccore_task_mapper.update_request_to_domain(update_request)
        updated_task = ccore_task_service.update_task(task)

    except ValueError as error:
        _send_validation_error(handler, str(error))
        return

    except Exception as error:
        _send_server_error(handler, error)
        return

    if updated_task is None:
        _send_not_found_error(handler)
        return

    _send_success(
        handler,
        200,
        {
            "message": CCORE_TASK_UPDATED_SUCCESS_MESSAGE,
            "task": ccore_task_mapper.domain_to_response(updated_task),
        },
    )


def handle_delete_ccore_task(handler, ccore_task_service, path: str) -> None:
    task_id = extract_ccore_task_id(path)

    try:
        deleted = ccore_task_service.delete_task(task_id)

    except ValueError as error:
        _send_validation_error(handler, str(error))
        return

    except Exception as error:
        _send_server_error(handler, error)
        return

    if not deleted:
        _send_not_found_error(handler)
        return

    _send_success(
        handler,
        200,
        {
            "message": CCORE_TASK_DELETED_SUCCESS_MESSAGE,
        },
    )


def handle_execute_ccore_task_path(
    handler,
    task_execution_service,
    path: str,
) -> None:
    task_id = extract_ccore_task_id_from_suffix_path(
        path,
        CCORE_TASK_EXECUTE_SUFFIX,
    )
    request_data = read_json_body(handler)

    if request_data is None:
        _send_validation_error(handler, CCORE_TASK_INVALID_JSON_BODY_MESSAGE)
        return

    execution_request = TaskExecutionRequest(
        task_id=task_id,
        execution_provider_id=int(request_data.get("providerId", 0)),
        execution_implementer_id=int(request_data.get("implementerId", 0)),
        requested_by=request_data.get("requestedBy", "system"),
        input_payload=request_data.get("inputPayload", {}),
    )

    try:
        result = task_execution_service.run_task(task_id, execution_request)

    except ValueError as error:
        _send_validation_error(handler, str(error))
        return

    except Exception as error:
        _send_server_error(handler, error)
        return

    status_code = 200

    if result.status == "FAILED":
        status_code = 500

    _send_success(
        handler,
        status_code,
        {
            "message": result.message,
            "execution": task_execution_result_to_response(result),
        },
    )


def handle_execute_ccore_task(
    handler,
    task_execution_service,
    path: str,
) -> None:
    handle_execute_ccore_task_path(handler, task_execution_service, path)


def task_execution_result_to_response(result: TaskExecutionResult) -> dict:
    return {
        "taskId": result.task_id,
        "status": result.status,
        "message": result.message,
        "providerName": result.provider_name,
        "implementerName": result.implementer_name,
        "executionDetails": result.execution_details,
        "errorDetails": result.error_details,
    }


def handle_get_ccore_task_executions(handler, ccore_task_service, path: str) -> None:
    task_id = extract_ccore_task_id_from_suffix_path(path, "/executions")

    try:
        executions = ccore_task_service.get_execution_history(task_id)

    except ValueError as error:
        _send_validation_error(handler, str(error))
        return

    except Exception as error:
        _send_server_error(handler, error)
        return

    _send_success(
        handler,
        200,
        {
            "executions": ccore_task_execution_mapper.domains_to_response(executions),
        },
    )


def extract_ccore_task_id(path: str) -> str:
    if not path.startswith(API_PATH_CCORE_TASKS_PREFIX):
        raise ValueError(CCORE_TASK_INVALID_ID_MESSAGE)

    task_id = unquote(path[len(API_PATH_CCORE_TASKS_PREFIX) :]).strip("/")

    if not task_id:
        raise ValueError(CCORE_TASK_INVALID_ID_MESSAGE)

    return task_id


def extract_ccore_task_id_from_suffix_path(path: str, suffix: str) -> str:
    if not path.endswith(suffix):
        raise ValueError(CCORE_TASK_INVALID_ID_MESSAGE)

    base_path = path[: -len(suffix)]
    return extract_ccore_task_id(base_path)
