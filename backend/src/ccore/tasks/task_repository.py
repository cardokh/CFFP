"""
CCore task PostgreSQL repository.

Responsibilities:
- Execute ccore_tasks CRUD queries.
- Map PostgreSQL rows to CCore task domain objects.
- Keep SQL access isolated from routes and services.
"""

from backend.src.ccore.infrastructure.database_contracts import (
    DatabaseConnectionProviderProtocol,
)
from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_constants import (
    CCORE_TASK_CREATED_AT_COLUMN,
    CCORE_TASK_ID_COLUMN,
    CCORE_TASK_NAME_COLUMN,
    CCORE_TASK_STATUS_CODE_COLUMN,
    CCORE_TASK_STATUS_LABEL_COLUMN,
    CCORE_TASK_STATUS_SORT_ORDER_COLUMN,
    CCORE_TASK_STATUSES_TABLE_NAME,
    CCORE_TASKS_TABLE_NAME,
)
from backend.src.ccore.tasks.task_status import CCoreTaskStatus


class CCoreTaskRepository:
    def __init__(self, db_manager: DatabaseConnectionProviderProtocol):
        self.db_manager = db_manager

    def _map_row_to_task(self, row) -> CCoreTask:
        return CCoreTask(
            task_id=str(row[0]),
            task_name=row[1],
            status_code=row[2],
            status_label=row[3],
            created_at=row[4].isoformat() if row[4] is not None else None,
        )

    def find_all_tasks(self) -> list[CCoreTask]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        task.{CCORE_TASK_ID_COLUMN},
                        task.{CCORE_TASK_NAME_COLUMN},
                        task.{CCORE_TASK_STATUS_CODE_COLUMN},
                        status.{CCORE_TASK_STATUS_LABEL_COLUMN},
                        task.{CCORE_TASK_CREATED_AT_COLUMN}
                    FROM {CCORE_TASKS_TABLE_NAME} task
                    INNER JOIN {CCORE_TASK_STATUSES_TABLE_NAME} status
                        ON status.{CCORE_TASK_STATUS_CODE_COLUMN} = task.{CCORE_TASK_STATUS_CODE_COLUMN}
                    ORDER BY task.{CCORE_TASK_CREATED_AT_COLUMN} DESC, task.{CCORE_TASK_NAME_COLUMN} ASC
                    """
                )

                rows = cursor.fetchall()

        return [self._map_row_to_task(row) for row in rows]

    def find_by_id(self, task_id: str) -> CCoreTask | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        task.{CCORE_TASK_ID_COLUMN},
                        task.{CCORE_TASK_NAME_COLUMN},
                        task.{CCORE_TASK_STATUS_CODE_COLUMN},
                        status.{CCORE_TASK_STATUS_LABEL_COLUMN},
                        task.{CCORE_TASK_CREATED_AT_COLUMN}
                    FROM {CCORE_TASKS_TABLE_NAME} task
                    INNER JOIN {CCORE_TASK_STATUSES_TABLE_NAME} status
                        ON status.{CCORE_TASK_STATUS_CODE_COLUMN} = task.{CCORE_TASK_STATUS_CODE_COLUMN}
                    WHERE task.{CCORE_TASK_ID_COLUMN} = %s
                    """,
                    (task_id,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row_to_task(row)

    def create_task(self, task: CCoreTask) -> CCoreTask:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {CCORE_TASKS_TABLE_NAME} (
                        {CCORE_TASK_ID_COLUMN},
                        {CCORE_TASK_NAME_COLUMN},
                        {CCORE_TASK_STATUS_CODE_COLUMN}
                    )
                    VALUES (
                        gen_random_uuid(),
                        %s,
                        %s
                    )
                    RETURNING
                        {CCORE_TASK_ID_COLUMN},
                        {CCORE_TASK_NAME_COLUMN},
                        {CCORE_TASK_STATUS_CODE_COLUMN},
                        (
                            SELECT {CCORE_TASK_STATUS_LABEL_COLUMN}
                            FROM {CCORE_TASK_STATUSES_TABLE_NAME}
                            WHERE {CCORE_TASK_STATUS_CODE_COLUMN} = {CCORE_TASKS_TABLE_NAME}.{CCORE_TASK_STATUS_CODE_COLUMN}
                        ) AS {CCORE_TASK_STATUS_LABEL_COLUMN},
                        {CCORE_TASK_CREATED_AT_COLUMN}
                    """,
                    (
                        task.task_name,
                        task.status_code,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        return self._map_row_to_task(row)

    def update_task(self, task: CCoreTask) -> CCoreTask | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {CCORE_TASKS_TABLE_NAME}
                    SET
                        {CCORE_TASK_NAME_COLUMN} = %s,
                        {CCORE_TASK_STATUS_CODE_COLUMN} = %s
                    WHERE {CCORE_TASK_ID_COLUMN} = %s
                    RETURNING
                        {CCORE_TASK_ID_COLUMN},
                        {CCORE_TASK_NAME_COLUMN},
                        {CCORE_TASK_STATUS_CODE_COLUMN},
                        (
                            SELECT {CCORE_TASK_STATUS_LABEL_COLUMN}
                            FROM {CCORE_TASK_STATUSES_TABLE_NAME}
                            WHERE {CCORE_TASK_STATUS_CODE_COLUMN} = {CCORE_TASKS_TABLE_NAME}.{CCORE_TASK_STATUS_CODE_COLUMN}
                        ) AS {CCORE_TASK_STATUS_LABEL_COLUMN},
                        {CCORE_TASK_CREATED_AT_COLUMN}
                    """,
                    (
                        task.task_name,
                        task.status_code,
                        task.task_id,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        if row is None:
            return None

        return self._map_row_to_task(row)

    def delete_task(self, task_id: str) -> bool:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {CCORE_TASKS_TABLE_NAME}
                    WHERE {CCORE_TASK_ID_COLUMN} = %s
                    """,
                    (task_id,),
                )

                deleted_count = cursor.rowcount

            connection.commit()

        return deleted_count > 0


class CCoreTaskStatusRepository:
    def __init__(self, db_manager: DatabaseConnectionProviderProtocol):
        self.db_manager = db_manager

    def _map_row_to_status(self, row) -> CCoreTaskStatus:
        return CCoreTaskStatus(
            status_code=row[0],
            status_label=row[1],
            sort_order=row[2],
        )

    def find_all_statuses(self) -> list[CCoreTaskStatus]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_TASK_STATUS_CODE_COLUMN},
                        {CCORE_TASK_STATUS_LABEL_COLUMN},
                        {CCORE_TASK_STATUS_SORT_ORDER_COLUMN}
                    FROM {CCORE_TASK_STATUSES_TABLE_NAME}
                    ORDER BY {CCORE_TASK_STATUS_SORT_ORDER_COLUMN} ASC, {CCORE_TASK_STATUS_LABEL_COLUMN} ASC
                    """
                )

                rows = cursor.fetchall()

        return [self._map_row_to_status(row) for row in rows]

    def status_exists(self, status_code: str) -> bool:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT 1
                    FROM {CCORE_TASK_STATUSES_TABLE_NAME}
                    WHERE {CCORE_TASK_STATUS_CODE_COLUMN} = %s
                    """,
                    (status_code,),
                )

                return cursor.fetchone() is not None
