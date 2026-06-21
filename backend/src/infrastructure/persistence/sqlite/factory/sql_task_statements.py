"""SQL statements for Factory task repository operations."""

from __future__ import annotations

SELECT_PENDING_TASKS_SQL = """
SELECT
    task_id,
    name,
    description,
    status,
    task_definition_path,
    priority,
    payload,
    created_at,
    updated_at,
    started_at,
    completed_at,
    error_message
FROM factory_tasks
WHERE status = ?
ORDER BY priority ASC, created_at ASC, task_id ASC
"""

UPSERT_TASK_SQL = """
INSERT INTO factory_tasks (
    task_id,
    name,
    description,
    status,
    task_definition_path,
    priority,
    payload
)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(task_id) DO UPDATE SET
    name = excluded.name,
    description = excluded.description,
    status = excluded.status,
    task_definition_path = excluded.task_definition_path,
    priority = excluded.priority,
    payload = excluded.payload,
    updated_at = CURRENT_TIMESTAMP,
    started_at = NULL,
    completed_at = NULL,
    error_message = NULL
"""


MARK_FACTORY_TASK_RUNNING_SQL = """
UPDATE factory_tasks
SET
    status = ?,
    started_at = CURRENT_TIMESTAMP,
    completed_at = NULL,
    error_message = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE task_id = ?
"""

MARK_FACTORY_TASK_COMPLETED_SQL = """
UPDATE factory_tasks
SET
    status = ?,
    completed_at = CURRENT_TIMESTAMP,
    error_message = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE task_id = ?
"""

MARK_FACTORY_TASK_FAILED_SQL = """
UPDATE factory_tasks
SET
    status = ?,
    completed_at = CURRENT_TIMESTAMP,
    error_message = ?,
    updated_at = CURRENT_TIMESTAMP
WHERE task_id = ?
"""
