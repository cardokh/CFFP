"""
CCore task execution PostgreSQL repository.

Responsibilities:
- Persist task execution records and reports.
- Read latest execution and execution history for CCore task details views.
- Keep SQL details isolated from services and route handlers.
"""

from psycopg2.extras import Json

from backend.src.ccore.infrastructure.database_contracts import (
    DatabaseConnectionProviderProtocol,
)
from backend.src.ccore.tasks.task_execution import CCoreTaskExecution
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_CREATED_AT_COLUMN,
    CCORE_TASK_EXECUTION_FINISHED_AT_COLUMN,
    CCORE_TASK_EXECUTION_ID_COLUMN,
    CCORE_TASK_EXECUTION_REPORT_JSON_COLUMN,
    CCORE_TASK_EXECUTION_RUNNER_CODE_COLUMN,
    CCORE_TASK_EXECUTION_STARTED_AT_COLUMN,
    CCORE_TASK_EXECUTION_STATUSES_TABLE_NAME,
    CCORE_TASK_EXECUTION_STATUS_CODE_COLUMN,
    CCORE_TASK_EXECUTION_STATUS_LABEL_COLUMN,
    CCORE_TASK_EXECUTION_TASK_ID_COLUMN,
    CCORE_TASK_EXECUTIONS_TABLE_NAME,
)


class CCoreTaskExecutionRepository:
    def __init__(self, db_manager: DatabaseConnectionProviderProtocol):
        self.db_manager = db_manager

    def _map_row_to_execution(self, row) -> CCoreTaskExecution:
        return CCoreTaskExecution(
            execution_id=str(row[0]),
            task_id=str(row[1]),
            status_code=row[2],
            status_label=row[3],
            runner_code=row[4],
            report_json=row[5],
            started_at=row[6].isoformat() if row[6] is not None else None,
            finished_at=row[7].isoformat() if row[7] is not None else None,
            created_at=row[8].isoformat() if row[8] is not None else None,
        )

    def _execution_select_columns(self) -> str:
        return f"""
            execution.{CCORE_TASK_EXECUTION_ID_COLUMN},
            execution.{CCORE_TASK_EXECUTION_TASK_ID_COLUMN},
            execution.{CCORE_TASK_EXECUTION_STATUS_CODE_COLUMN},
            status.{CCORE_TASK_EXECUTION_STATUS_LABEL_COLUMN},
            execution.{CCORE_TASK_EXECUTION_RUNNER_CODE_COLUMN},
            execution.{CCORE_TASK_EXECUTION_REPORT_JSON_COLUMN},
            execution.{CCORE_TASK_EXECUTION_STARTED_AT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_FINISHED_AT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_CREATED_AT_COLUMN}
        """

    def create_execution(self, execution: CCoreTaskExecution) -> CCoreTaskExecution:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {CCORE_TASK_EXECUTIONS_TABLE_NAME} (
                        {CCORE_TASK_EXECUTION_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_TASK_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_STATUS_CODE_COLUMN},
                        {CCORE_TASK_EXECUTION_RUNNER_CODE_COLUMN},
                        {CCORE_TASK_EXECUTION_REPORT_JSON_COLUMN},
                        {CCORE_TASK_EXECUTION_STARTED_AT_COLUMN},
                        {CCORE_TASK_EXECUTION_FINISHED_AT_COLUMN}
                    )
                    VALUES (
                        gen_random_uuid(),
                        %s,
                        %s,
                        %s,
                        %s,
                        COALESCE(%s, CURRENT_TIMESTAMP),
                        COALESCE(%s, CURRENT_TIMESTAMP)
                    )
                    RETURNING {CCORE_TASK_EXECUTION_ID_COLUMN}
                    """,
                    (
                        execution.task_id,
                        execution.status_code,
                        execution.runner_code,
                        Json(execution.report_json or {}),
                        execution.started_at,
                        execution.finished_at,
                    ),
                )
                execution_id = str(cursor.fetchone()[0])
            connection.commit()

        created_execution = self.find_by_execution_id(execution_id)

        if created_execution is None:
            raise RuntimeError(f"Created CCore task execution could not be read: {execution_id}")

        return created_execution

    def find_by_execution_id(self, execution_id: str) -> CCoreTaskExecution | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._execution_select_columns()}
                    FROM {CCORE_TASK_EXECUTIONS_TABLE_NAME} execution
                    INNER JOIN {CCORE_TASK_EXECUTION_STATUSES_TABLE_NAME} status
                        ON status.{CCORE_TASK_EXECUTION_STATUS_CODE_COLUMN} = execution.{CCORE_TASK_EXECUTION_STATUS_CODE_COLUMN}
                    WHERE execution.{CCORE_TASK_EXECUTION_ID_COLUMN} = %s
                    """,
                    (execution_id,),
                )
                row = cursor.fetchone()

        return self._map_row_to_execution(row) if row is not None else None

    def find_latest_by_task_id(self, task_id: str) -> CCoreTaskExecution | None:
        executions = self._find_by_task_id(task_id=task_id, limit=1)
        return executions[0] if executions else None

    def find_by_task_id(self, task_id: str) -> list[CCoreTaskExecution]:
        return self._find_by_task_id(task_id=task_id, limit=None)

    def _find_by_task_id(self, task_id: str, limit: int | None) -> list[CCoreTaskExecution]:
        limit_clause = "LIMIT %s" if limit is not None else ""
        parameters = [task_id]

        if limit is not None:
            parameters.append(limit)

        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._execution_select_columns()}
                    FROM {CCORE_TASK_EXECUTIONS_TABLE_NAME} execution
                    INNER JOIN {CCORE_TASK_EXECUTION_STATUSES_TABLE_NAME} status
                        ON status.{CCORE_TASK_EXECUTION_STATUS_CODE_COLUMN} = execution.{CCORE_TASK_EXECUTION_STATUS_CODE_COLUMN}
                    WHERE execution.{CCORE_TASK_EXECUTION_TASK_ID_COLUMN} = %s
                    ORDER BY execution.{CCORE_TASK_EXECUTION_CREATED_AT_COLUMN} DESC
                    {limit_clause}
                    """,
                    tuple(parameters),
                )
                rows = cursor.fetchall()

        return [self._map_row_to_execution(row) for row in rows]
