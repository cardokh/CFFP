"""SQLite implementation of the Factory task repository."""

from __future__ import annotations

from sqlite3 import Connection, Row

from src.core.infrastructure.database import DatabaseManager

from .sql_task_schema import (
    CREATE_FACTORY_TASKS_STATUS_INDEX_SQL,
    CREATE_FACTORY_TASKS_TABLE_SQL,
)
from .sql_task_mapper import map_factory_task_row
from .sql_task_statements import SELECT_PENDING_TASKS_SQL, UPSERT_TASK_SQL
from .task_models import FactoryTask
from .task_status import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
)


class SqlTaskRepository:
    """Stores Factory task lifecycle state in SQLite."""

    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    def initialize_schema(self) -> None:
        """Create Factory task tables and indexes."""

        with self._connect() as connection:
            connection.execute(CREATE_FACTORY_TASKS_TABLE_SQL)
            connection.execute(CREATE_FACTORY_TASKS_STATUS_INDEX_SQL)
            connection.commit()

    def find_pending_tasks(self) -> tuple[FactoryTask, ...]:
        """Return pending Factory tasks ordered for execution."""

        with self._connect() as connection:
            rows = connection.execute(SELECT_PENDING_TASKS_SQL, (TASK_STATUS_PENDING,)).fetchall()

        return tuple(map_factory_task_row(row) for row in rows)

    def upsert_task(self, task: FactoryTask) -> None:
        """Create or update one Factory task."""

        with self._connect() as connection:
            connection.execute(
                UPSERT_TASK_SQL,
                (
                    task.task_id,
                    task.name,
                    task.description,
                    task.status,
                    task.task_definition_path,
                    task.priority,
                ),
            )
            connection.commit()

    def mark_running(self, task_id: str) -> None:
        """Mark one task as running."""

        self._update_status(task_id, TASK_STATUS_RUNNING, started=True)

    def mark_completed(self, task_id: str) -> None:
        """Mark one task as completed."""

        self._update_status(task_id, TASK_STATUS_COMPLETED, completed=True)

    def mark_failed(self, task_id: str, error_message: str) -> None:
        """Mark one task as failed."""

        self._update_status(
            task_id,
            TASK_STATUS_FAILED,
            completed=True,
            error_message=error_message,
        )

    def _update_status(
        self,
        task_id: str,
        status: str,
        *,
        started: bool = False,
        completed: bool = False,
        error_message: str | None = None,
    ) -> None:
        started_sql = "started_at = CURRENT_TIMESTAMP," if started else ""
        completed_sql = "completed_at = CURRENT_TIMESTAMP," if completed else ""
        with self._connect() as connection:
            connection.execute(
                f"""
                UPDATE factory_tasks
                SET
                    status = ?,
                    {started_sql}
                    {completed_sql}
                    error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
                """,
                (status, error_message, task_id),
            )
            connection.commit()

    def _connect(self) -> Connection:
        connection = self.database_manager.get_connection()
        connection.row_factory = Row
        return connection
