"""
Automation task API contracts.

Responsibilities:
- Centralize transport field names for automation task responses.
- Keep response dictionaries consistent across routes, mappers, and tests.
"""

AUTOMATION_TASK_RESPONSE_TASK = "task"
AUTOMATION_TASK_RESPONSE_TASKS = "tasks"
AUTOMATION_TASK_RESPONSE_CONFIGURATION = "configuration"
AUTOMATION_TASK_RESPONSE_CONFIGURATION_PATH = "configuration_path"

AUTOMATION_TASK_ID = "id"
AUTOMATION_TASK_NAME = "name"
AUTOMATION_TASK_DESCRIPTION = "description"
AUTOMATION_TASK_CATEGORY = "category"
AUTOMATION_TASK_STATUS = "status"
AUTOMATION_TASK_SCRIPT_PATH = "script_path"
AUTOMATION_TASK_CONFIG_PATH = "config_path"
