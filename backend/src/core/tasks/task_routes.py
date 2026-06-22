"""
CCore task API routes.

Responsibilities:
- Handle CCore task CRUD HTTP requests.
- Convert JSON requests into task request contracts.
- Delegate business use cases to CCoreTaskService.
- Return consistent JSON responses.
"""

from urllib.parse import unquote

from src.api.api_paths import API_PATH_CCORE_TASKS_PREFIX
from src.api.route_utils import read_json_body, send_json
from src.core.tasks.task_contracts import (
    CreateCCoreTaskRequest,
    UpdateCCoreTaskRequest,
)
from src.core.tasks.task_mapper import CCoreTaskMapper
from src.core.tasks.task_messages import (
    CCORE_TASK_CREATED_SUCCESS_MESSAGE,
    CCORE_TASK_DELETED_SUCCESS_MESSAGE,
    CCORE_TASK_INVALID_ID_MESSAGE,
    CCORE_TASK_INVALID_JSON_BODY_MESSAGE,
    CCORE_TASK_NOT_FOUND_MESSAGE,
    CCORE_TASK_UPDATED_SUCCESS_MESSAGE,
)

ccore_task_mapper = CCoreTaskMapper()


def handle_get_ccore_tasks(handler, ccore_task_service) -> None:
    try:
        tasks = ccore_task_service.get_all_tasks()

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "tasks": ccore_task_mapper.domains_to_response(tasks),
        },
    )


def handle_get_ccore_task_by_id(handler, ccore_task_service, path: str) -> None:
    task_id = extract_ccore_task_id(path)

    try:
        task = ccore_task_service.get_task_by_id(task_id)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    if task is None:
        send_json(handler, 404, {"success": False, "error": CCORE_TASK_NOT_FOUND_MESSAGE})
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "task": ccore_task_mapper.domain_to_response(task),
        },
    )


def handle_create_ccore_task(handler, ccore_task_service) -> None:
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(handler, 400, {"success": False, "error": CCORE_TASK_INVALID_JSON_BODY_MESSAGE})
        return

    try:
        create_request = CreateCCoreTaskRequest(
            task_name=request_data.get("taskName", request_data.get("name", "")),
            status=request_data.get("status", "PENDING"),
        )

        task = ccore_task_mapper.create_request_to_domain(create_request)
        created_task = ccore_task_service.create_task(task)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    send_json(
        handler,
        201,
        {
            "success": True,
            "message": CCORE_TASK_CREATED_SUCCESS_MESSAGE,
            "task": ccore_task_mapper.domain_to_response(created_task),
        },
    )


def handle_update_ccore_task(handler, ccore_task_service, path: str) -> None:
    task_id = extract_ccore_task_id(path)
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(handler, 400, {"success": False, "error": CCORE_TASK_INVALID_JSON_BODY_MESSAGE})
        return

    try:
        update_request = UpdateCCoreTaskRequest(
            task_id=task_id,
            task_name=request_data.get("taskName", request_data.get("name", "")),
            status=request_data.get("status", ""),
        )

        task = ccore_task_mapper.update_request_to_domain(update_request)
        updated_task = ccore_task_service.update_task(task)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    if updated_task is None:
        send_json(handler, 404, {"success": False, "error": CCORE_TASK_NOT_FOUND_MESSAGE})
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": CCORE_TASK_UPDATED_SUCCESS_MESSAGE,
            "task": ccore_task_mapper.domain_to_response(updated_task),
        },
    )


def handle_delete_ccore_task(handler, ccore_task_service, path: str) -> None:
    task_id = extract_ccore_task_id(path)

    try:
        deleted = ccore_task_service.delete_task(task_id)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    if not deleted:
        send_json(handler, 404, {"success": False, "error": CCORE_TASK_NOT_FOUND_MESSAGE})
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": CCORE_TASK_DELETED_SUCCESS_MESSAGE,
        },
    )


def extract_ccore_task_id(path: str) -> str:
    if not path.startswith(API_PATH_CCORE_TASKS_PREFIX):
        raise ValueError(CCORE_TASK_INVALID_ID_MESSAGE)

    task_id = unquote(path[len(API_PATH_CCORE_TASKS_PREFIX):]).strip("/")

    if not task_id:
        raise ValueError(CCORE_TASK_INVALID_ID_MESSAGE)

    return task_id
