"""SQL schema statements for Factory task persistence."""

from __future__ import annotations

FACTORY_TASKS_TABLE = "factory_tasks"

CREATE_FACTORY_TASKS_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {FACTORY_TASKS_TABLE} (
    task_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    task_definition_path TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    payload TEXT NOT NULL DEFAULT '{{}}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT
)
"""

CREATE_FACTORY_TASKS_STATUS_INDEX_SQL = f"""
CREATE INDEX IF NOT EXISTS idx_{FACTORY_TASKS_TABLE}_status_priority
ON {FACTORY_TASKS_TABLE} (status, priority, created_at)
"""


ADD_FACTORY_TASKS_PAYLOAD_COLUMN_SQL = """
ALTER TABLE factory_tasks
ADD COLUMN payload TEXT NOT NULL DEFAULT '{}'
"""
