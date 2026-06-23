"""
CCore task response and validation messages.

Responsibilities:
- Centralize task-related API and validation messages.
- Avoid duplicated response strings across route handlers, services, and validators.
"""

CCORE_TASK_CREATED_SUCCESS_MESSAGE = "CCore task created successfully."
CCORE_TASK_UPDATED_SUCCESS_MESSAGE = "CCore task updated successfully."
CCORE_TASK_DELETED_SUCCESS_MESSAGE = "CCore task deleted successfully."

CCORE_TASK_NOT_FOUND_MESSAGE = "CCore task was not found."

CCORE_TASK_INVALID_ID_MESSAGE = "A valid CCore task id is required."
CCORE_TASK_ID_REQUIRED_MESSAGE = CCORE_TASK_INVALID_ID_MESSAGE

CCORE_TASK_INVALID_JSON_BODY_MESSAGE = "Request body must contain valid JSON."
CCORE_TASK_PAYLOAD_OBJECT_REQUIRED_MESSAGE = "Request body must be a JSON object."

CCORE_TASK_UNKNOWN_FIELD_MESSAGE = "Unsupported task request field."

CCORE_TASK_NAME_REQUIRED_MESSAGE = "Task name is required."
CCORE_TASK_STATUS_REQUIRED_MESSAGE = "Task status is required."
CCORE_TASK_STATUS_INVALID_MESSAGE = "Task status is not valid."

CCORE_TASK_ERROR_CODE_VALIDATION = "CCORE_TASK_VALIDATION_ERROR"
CCORE_TASK_ERROR_CODE_NOT_FOUND = "CCORE_TASK_NOT_FOUND"
CCORE_TASK_ERROR_CODE_SERVER = "CCORE_TASK_SERVER_ERROR"
