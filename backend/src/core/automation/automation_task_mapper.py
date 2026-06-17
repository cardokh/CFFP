"""
Automation task mapper.

Responsibilities:
- Convert automation task domain objects into API response dictionaries.
- Convert task configuration data into API response dictionaries.
- Keep transport field names out of routes and services.
"""

from src.core.automation.automation_task_contracts import (
    AUTOMATION_TASK_CATEGORY,
    AUTOMATION_TASK_CONFIG_PATH,
    AUTOMATION_TASK_DESCRIPTION,
    AUTOMATION_TASK_ID,
    AUTOMATION_TASK_NAME,
    AUTOMATION_TASK_RESPONSE_CONFIGURATION,
    AUTOMATION_TASK_RESPONSE_CONFIGURATION_PATH,
    AUTOMATION_TASK_RESPONSE_TASK,
    AUTOMATION_TASK_RESPONSE_TASKS,
    AUTOMATION_TASK_SCRIPT_PATH,
    AUTOMATION_TASK_STATUS,
)


def automation_task_to_response(automation_task) -> dict:
    return {
        AUTOMATION_TASK_ID: automation_task.task_id,
        AUTOMATION_TASK_NAME: automation_task.name,
        AUTOMATION_TASK_DESCRIPTION: automation_task.description,
        AUTOMATION_TASK_CATEGORY: automation_task.category,
        AUTOMATION_TASK_STATUS: automation_task.status,
        AUTOMATION_TASK_SCRIPT_PATH: automation_task.script_path,
        AUTOMATION_TASK_CONFIG_PATH: automation_task.config_path,
    }


def automation_task_detail_to_response(automation_task) -> dict:
    return {
        AUTOMATION_TASK_RESPONSE_TASK: automation_task_to_response(
            automation_task
        ),
    }


def automation_task_configuration_to_response(task_configuration_result) -> dict:
    automation_task = task_configuration_result["task"]

    return {
        AUTOMATION_TASK_RESPONSE_TASK: automation_task_to_response(
            automation_task,
        ),
        AUTOMATION_TASK_RESPONSE_CONFIGURATION_PATH: automation_task.config_path,
        AUTOMATION_TASK_RESPONSE_CONFIGURATION: task_configuration_result[
            "configuration"
        ],
    }


def automation_tasks_to_response(automation_tasks: list) -> dict:
    return {
        AUTOMATION_TASK_RESPONSE_TASKS: [
            automation_task_to_response(automation_task)
            for automation_task in automation_tasks
        ],
    }
