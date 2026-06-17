"""
Automation task API routes.

Responsibilities:
- Handle automation task HTTP requests.
- Delegate task discovery to AutomationTaskService.
- Return registered automation task metadata for the automation dashboard.
"""

from json import JSONDecodeError
from urllib.parse import unquote

from src.api.api_paths import API_PATH_AUTOMATION_TASKS_PREFIX
from src.api.route_utils import send_json
from src.core.automation.automation_task_mapper import (
    automation_task_detail_to_response,
    automation_tasks_to_response,
)
from src.core.automation.automation_task_messages import (
    AUTOMATION_TASK_NOT_FOUND,
    AUTOMATION_TASK_REGISTRY_INVALID,
    AUTOMATION_TASK_REGISTRY_LOAD_FAILED,
)


def handle_get_automation_tasks(handler, automation_task_service) -> None:
    try:
        automation_tasks = automation_task_service.get_all_tasks()

    except FileNotFoundError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_TASK_REGISTRY_LOAD_FAILED,
            },
        )
        return

    except JSONDecodeError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_TASK_REGISTRY_INVALID,
            },
        )
        return

    response = automation_tasks_to_response(automation_tasks)

    send_json(
        handler,
        200,
        response,
    )


def handle_get_automation_task_by_id(
    handler,
    automation_task_service,
    path,
) -> None:
    task_id = extract_automation_task_id_from_path(path)

    try:
        automation_task = automation_task_service.get_task_by_id(
            task_id=task_id,
        )

    except FileNotFoundError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_TASK_REGISTRY_LOAD_FAILED,
            },
        )
        return

    except JSONDecodeError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_TASK_REGISTRY_INVALID,
            },
        )
        return

    if automation_task is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": AUTOMATION_TASK_NOT_FOUND,
            },
        )
        return

    response = automation_task_detail_to_response(
        automation_task
    )

    send_json(
        handler,
        200,
        response,
    )


def extract_automation_task_id_from_path(path: str) -> str:
    return unquote(
        path.replace(
            API_PATH_AUTOMATION_TASKS_PREFIX,
            "",
            1,
        ).strip()
    )
