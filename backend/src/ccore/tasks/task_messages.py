"""
CCore task response and validation messages.

Responsibilities:
- Centralize task-related API and validation messages.
- Avoid duplicated response strings across route handlers and validators.
"""

CCORE_TASK_CREATED_SUCCESS_MESSAGE = "CCore task created successfully."
CCORE_TASK_UPDATED_SUCCESS_MESSAGE = "CCore task updated successfully."
CCORE_TASK_DELETED_SUCCESS_MESSAGE = "CCore task deleted successfully."

CCORE_TASK_NOT_FOUND_MESSAGE = "CCore task was not found."
CCORE_TASK_INVALID_ID_MESSAGE = "A valid CCore task id is required."
CCORE_TASK_INVALID_JSON_BODY_MESSAGE = "Request body must contain valid JSON."

CCORE_TASK_NAME_REQUIRED_MESSAGE = "Task name is required."
CCORE_TASK_STATUS_REQUIRED_MESSAGE = "Task status is required."
CCORE_TASK_STATUS_INVALID_MESSAGE = "Task status is not valid."
