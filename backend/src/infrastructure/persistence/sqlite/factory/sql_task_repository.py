"""SQLite implementation of the Factory task repository."""

from __future__ import annotations

from sqlite3 import Connection, Row

from backend.src.ccore.infrastructure.database import DatabaseManager

from src.infrastructure.persistence.sqlite.factory.sql_task_schema import (
    ADD_FACTORY_TASKS_PAYLOAD_COLUMN_SQL,
    CREATE_FACTORY_TASKS_STATUS_INDEX_SQL,
    CREATE_FACTORY_TASKS_TABLE_SQL,
)
from src.infrastructure.persistence.sqlite.factory.sql_task_mapper import (
    map_factory_task_row,
)
from src.infrastructure.persistence.sqlite.factory.sql_task_statements import (
    MARK_FACTORY_TASK_COMPLETED_SQL,
    MARK_FACTORY_TASK_FAILED_SQL,
    MARK_FACTORY_TASK_RUNNING_SQL,
    SELECT_PENDING_TASKS_SQL,
    UPSERT_TASK_SQL,
)
from src.core.factory.task_models import FactoryTask
from src.core.factory.task_status import (
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
            self._ensure_payload_column(connection)
            connection.execute(CREATE_FACTORY_TASKS_STATUS_INDEX_SQL)
            connection.commit()

    def find_pending_tasks(self) -> tuple[FactoryTask, ...]:
        """Return pending Factory tasks ordered for execution."""

        with self._connect() as connection:
            rows = connection.execute(
                SELECT_PENDING_TASKS_SQL, (TASK_STATUS_PENDING,)
            ).fetchall()

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
                    task.payload,
                ),
            )
            connection.commit()

    def mark_running(self, task_id: str) -> None:
        """Mark one task as running."""

        with self._connect() as connection:
            connection.execute(
                MARK_FACTORY_TASK_RUNNING_SQL, (TASK_STATUS_RUNNING, task_id)
            )
            connection.commit()

    def mark_completed(self, task_id: str) -> None:
        """Mark one task as completed."""

        with self._connect() as connection:
            connection.execute(
                MARK_FACTORY_TASK_COMPLETED_SQL, (TASK_STATUS_COMPLETED, task_id)
            )
            connection.commit()

    def mark_failed(self, task_id: str, error_message: str) -> None:
        """Mark one task as failed."""

        with self._connect() as connection:
            connection.execute(
                MARK_FACTORY_TASK_FAILED_SQL,
                (TASK_STATUS_FAILED, error_message, task_id),
            )
            connection.commit()

    def _ensure_payload_column(self, connection: Connection) -> None:
        existing_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(factory_tasks)").fetchall()
        }
        if "payload" not in existing_columns:
            connection.execute(ADD_FACTORY_TASKS_PAYLOAD_COLUMN_SQL)

    def _connect(self) -> Connection:
        connection = self.database_manager.get_connection()
        connection.row_factory = Row
        return connection
