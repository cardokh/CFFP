"""SQLite row mapping for Factory tasks."""

from __future__ import annotations

from sqlite3 import Row

from .task_models import FactoryTask


def map_factory_task_row(row: Row) -> FactoryTask:
    """Map one SQLite row to a FactoryTask."""

    return FactoryTask(
        task_id=str(row["task_id"]),
        name=str(row["name"]),
        description=str(row["description"]),
        status=str(row["status"]),
        task_definition_path=str(row["task_definition_path"]),
        priority=int(row["priority"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
        error_message=row["error_message"],
    )
