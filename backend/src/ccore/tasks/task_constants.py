"""
CCore task constants.

Responsibilities:
- Centralize task table names, column names, lookup IDs, and API field names.
- Avoid duplicated literal values across repositories, services, routes, and mappers.
- Keep task-specific constants inside the CCore task boundary.
"""

CCORE_TASKS_TABLE_NAME = "ccore_tasks"
CCORE_TASK_STATUSES_TABLE_NAME = "ccore_task_statuses"

CCORE_TASK_ID_COLUMN = "task_id"
CCORE_TASK_NAME_COLUMN = "task_name"
CCORE_TASK_STATUS_ID_COLUMN = "status_id"
CCORE_TASK_CREATED_AT_COLUMN = "created_at"
CCORE_TASK_UPDATED_AT_COLUMN = "updated_at"

CCORE_TASK_STATUS_LABEL_COLUMN = "status_label"
CCORE_TASK_STATUS_SORT_ORDER_COLUMN = "sort_order"

CCORE_TASK_STATUS_ID_PENDING = 1
CCORE_TASK_STATUS_ID_RUNNING = 2
CCORE_TASK_STATUS_ID_COMPLETED = 3
CCORE_TASK_STATUS_ID_FAILED = 4

CCORE_TASK_API_FIELD_TASK_ID = "taskId"
CCORE_TASK_API_FIELD_TASK_NAME = "taskName"
CCORE_TASK_API_FIELD_STATUS = "status"
CCORE_TASK_API_FIELD_STATUS_ID = "statusId"
CCORE_TASK_API_FIELD_STATUS_LABEL = "statusLabel"
CCORE_TASK_API_FIELD_CREATED_AT = "createdAt"
CCORE_TASK_API_FIELD_UPDATED_AT = "updatedAt"

CCORE_TASK_STATUS_API_FIELD_ID = "id"
CCORE_TASK_STATUS_API_FIELD_LABEL = "label"
CCORE_TASK_STATUS_API_FIELD_SORT_ORDER = "sortOrder"
