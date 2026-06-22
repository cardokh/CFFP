"""
CCore task PostgreSQL repository.

Responsibilities:
- Execute ccore_tasks CRUD queries.
- Map PostgreSQL rows to CCore task domain objects.
- Keep SQL access isolated from routes and services.
"""

from backend.src.ccore.infrastructure.postgres_database import PostgresDatabaseManager
from backend.src.ccore.tasks.task import CCoreTask


class CCoreTaskRepository:
    def __init__(self, db_manager: PostgresDatabaseManager):
        self.db_manager = db_manager

    def _map_row_to_task(self, row) -> CCoreTask:
        return CCoreTask(
            task_id=str(row[0]),
            task_name=row[1],
            status=row[2],
            created_at=row[3].isoformat() if row[3] is not None else None,
        )

    def find_all_tasks(self) -> list[CCoreTask]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        task_id,
                        task_name,
                        status,
                        created_at
                    FROM ccore_tasks
                    ORDER BY created_at DESC, task_name ASC
                    """)

                rows = cursor.fetchall()

        return [self._map_row_to_task(row) for row in rows]

    def find_by_id(self, task_id: str) -> CCoreTask | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        task_id,
                        task_name,
                        status,
                        created_at
                    FROM ccore_tasks
                    WHERE task_id = %s
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
                    """
                    INSERT INTO ccore_tasks (
                        task_id,
                        task_name,
                        status
                    )
                    VALUES (
                        gen_random_uuid(),
                        %s,
                        %s
                    )
                    RETURNING
                        task_id,
                        task_name,
                        status,
                        created_at
                    """,
                    (
                        task.task_name,
                        task.status,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        return self._map_row_to_task(row)

    def update_task(self, task: CCoreTask) -> CCoreTask | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE ccore_tasks
                    SET
                        task_name = %s,
                        status = %s
                    WHERE task_id = %s
                    RETURNING
                        task_id,
                        task_name,
                        status,
                        created_at
                    """,
                    (
                        task.task_name,
                        task.status,
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
                    """
                    DELETE FROM ccore_tasks
                    WHERE task_id = %s
                    """,
                    (task_id,),
                )

                deleted_count = cursor.rowcount

            connection.commit()

        return deleted_count > 0
