"""
Automation task API routes.

Responsibilities:
- Handle automation task HTTP requests.
- Delegate task discovery to AutomationTaskService.
- Return registered automation task metadata for the automation dashboard.
"""

from json import JSONDecodeError

from src.api.route_utils import send_json
from src.core.automation.automation_task_mapper import (
    automation_tasks_to_response,
)
from src.core.automation.automation_task_messages import (
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
