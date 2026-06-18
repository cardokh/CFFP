"""
Automation task API routes.

Responsibilities:
- Handle automation task HTTP requests.
- Delegate task discovery and configuration loading to AutomationTaskService.
- Return registered automation task metadata and inspect-only configuration data.
"""

from json import JSONDecodeError
from urllib.parse import unquote

from src.api.api_paths import API_PATH_AUTOMATION_TASKS_PREFIX
from src.api.route_utils import send_json
from src.core.automation.automation_task_execution_mapper import (
    automation_task_execution_to_response,
)
from src.core.automation.automation_task_mapper import (
    automation_task_configuration_to_response,
    automation_task_validation_to_response,
    automation_task_detail_to_response,
    automation_tasks_to_response,
)
from src.core.automation.automation_task_messages import (
    AUTOMATION_TASK_CONFIGURATION_INVALID,
    AUTOMATION_TASK_CONFIGURATION_LOAD_FAILED,
    AUTOMATION_TASK_NOT_FOUND,
    AUTOMATION_TASK_REGISTRY_INVALID,
    AUTOMATION_TASK_REGISTRY_LOAD_FAILED,
)

AUTOMATION_TASK_CONFIGURATION_PATH_SUFFIX = "/configuration"
AUTOMATION_TASK_VALIDATE_PATH_SUFFIX = "/validate"
AUTOMATION_TASK_EXECUTE_PATH_SUFFIX = "/execute"


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


def handle_get_automation_task_path(
    handler,
    automation_task_service,
    path,
) -> None:
    if is_automation_task_configuration_path(path):
        handle_get_automation_task_configuration(
            handler,
            automation_task_service,
            path,
        )
        return

    handle_get_automation_task_by_id(
        handler,
        automation_task_service,
        path,
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


def handle_get_automation_task_configuration(
    handler,
    automation_task_service,
    path,
) -> None:
    task_id = extract_automation_task_id_from_configuration_path(path)

    try:
        task_configuration_result = automation_task_service.get_task_configuration_by_id(
            task_id=task_id,
        )

    except FileNotFoundError:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": AUTOMATION_TASK_CONFIGURATION_LOAD_FAILED,
            },
        )
        return

    except JSONDecodeError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_TASK_CONFIGURATION_INVALID,
            },
        )
        return

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if task_configuration_result is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": AUTOMATION_TASK_NOT_FOUND,
            },
        )
        return

    response = automation_task_configuration_to_response(
        task_configuration_result,
    )

    send_json(
        handler,
        200,
        response,
    )



def handle_validate_automation_task_path(
    handler,
    automation_task_service,
    path,
) -> None:
    if not is_automation_task_validate_path(path):
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": AUTOMATION_TASK_NOT_FOUND,
            },
        )
        return

    task_id = extract_automation_task_id_from_validate_path(path)

    try:
        task_validation_result = automation_task_service.validate_task_by_id(
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

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if task_validation_result is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": AUTOMATION_TASK_NOT_FOUND,
            },
        )
        return

    response = automation_task_validation_to_response(
        task_validation_result,
    )

    send_json(
        handler,
        200,
        response,
    )


def handle_execute_automation_task_path(
    handler,
    automation_task_service,
    path,
) -> None:
    if not is_automation_task_execute_path(path):
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": AUTOMATION_TASK_NOT_FOUND,
            },
        )
        return

    task_id = extract_automation_task_id_from_execute_path(path)

    try:
        task_execution_result = automation_task_service.execute_task_by_id(
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

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if task_execution_result is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": AUTOMATION_TASK_NOT_FOUND,
            },
        )
        return

    response = automation_task_execution_to_response(
        task_execution_result,
    )

    send_json(
        handler,
        200,
        response,
    )

def is_automation_task_configuration_path(path: str) -> bool:
    return path.endswith(AUTOMATION_TASK_CONFIGURATION_PATH_SUFFIX)


def is_automation_task_validate_path(path: str) -> bool:
    return path.endswith(AUTOMATION_TASK_VALIDATE_PATH_SUFFIX)


def is_automation_task_execute_path(path: str) -> bool:
    return path.endswith(AUTOMATION_TASK_EXECUTE_PATH_SUFFIX)


def extract_automation_task_id_from_path(path: str) -> str:
    return unquote(
        path.replace(
            API_PATH_AUTOMATION_TASKS_PREFIX,
            "",
            1,
        ).strip()
    )


def extract_automation_task_id_from_configuration_path(path: str) -> str:
    task_id_with_suffix = extract_automation_task_id_from_path(
        path,
    )

    return task_id_with_suffix.removesuffix(
        AUTOMATION_TASK_CONFIGURATION_PATH_SUFFIX.lstrip("/"),
    ).rstrip("/")


def extract_automation_task_id_from_validate_path(path: str) -> str:
    task_id_with_suffix = extract_automation_task_id_from_path(
        path,
    )

    return task_id_with_suffix.removesuffix(
        AUTOMATION_TASK_VALIDATE_PATH_SUFFIX.lstrip("/"),
    ).rstrip("/")


def extract_automation_task_id_from_execute_path(path: str) -> str:
    task_id_with_suffix = extract_automation_task_id_from_path(
        path,
    )

    return task_id_with_suffix.removesuffix(
        AUTOMATION_TASK_EXECUTE_PATH_SUFFIX.lstrip("/"),
    ).rstrip("/")
