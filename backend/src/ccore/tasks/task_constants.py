"""
CCore task constants.

Responsibilities:
- Centralize task table names, column names, default values, and API field names.
- Avoid duplicated literal values across repositories, services, routes, and mappers.
- Keep task-specific constants inside the CCore task boundary.
"""

CCORE_TASKS_TABLE_NAME = "ccore_tasks"
CCORE_TASK_STATUSES_TABLE_NAME = "ccore_task_statuses"

CCORE_TASK_ID_COLUMN = "task_id"
CCORE_TASK_NAME_COLUMN = "task_name"
CCORE_TASK_STATUS_CODE_COLUMN = "status_code"
CCORE_TASK_CREATED_AT_COLUMN = "created_at"

CCORE_TASK_STATUS_CODE_COLUMN_ALIAS = "status"
CCORE_TASK_STATUS_LABEL_COLUMN = "status_label"
CCORE_TASK_STATUS_SORT_ORDER_COLUMN = "sort_order"

CCORE_TASK_DEFAULT_STATUS_CODE = "PENDING"

CCORE_TASK_API_FIELD_ID = "id"
CCORE_TASK_API_FIELD_TASK_ID = "taskId"
CCORE_TASK_API_FIELD_NAME = "name"
CCORE_TASK_API_FIELD_TASK_NAME = "taskName"
CCORE_TASK_API_FIELD_STATUS = "status"
CCORE_TASK_API_FIELD_STATUS_LABEL = "statusLabel"
CCORE_TASK_API_FIELD_CREATED_AT = "createdAt"

CCORE_TASK_STATUS_API_FIELD_CODE = "code"
CCORE_TASK_STATUS_API_FIELD_LABEL = "label"
CCORE_TASK_STATUS_API_FIELD_SORT_ORDER = "sortOrder"
