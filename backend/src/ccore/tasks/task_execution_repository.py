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
    CCORE_TASK_EXECUTION_COMPLETED_AT_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_SNAPSHOT_COLUMN,
    CCORE_TASK_EXECUTION_CREATED_AT_COLUMN,
    CCORE_TASK_EXECUTION_ERROR_DETAILS_COLUMN,
    CCORE_TASK_EXECUTION_FAILED_AT_COLUMN,
    CCORE_TASK_EXECUTION_ID_COLUMN,
    CCORE_TASK_EXECUTION_INPUT_PAYLOAD_COLUMN,
    CCORE_TASK_EXECUTION_MODE_COLUMN,
    CCORE_TASK_EXECUTION_PROVIDER_PROFILE_COLUMN,
    CCORE_TASK_EXECUTION_REPORT_COLUMN,
    CCORE_TASK_EXECUTION_REQUESTED_BY_COLUMN,
    CCORE_TASK_EXECUTION_STARTED_AT_COLUMN,
    CCORE_TASK_EXECUTION_STATUSES_TABLE_NAME,
    CCORE_TASK_EXECUTION_STATUS_ID_COLUMN,
    CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED,
    CCORE_TASK_EXECUTION_STATUS_ID_FAILED,
    CCORE_TASK_EXECUTION_STATUS_LABEL_COLUMN,
    CCORE_TASK_EXECUTION_TASK_ID_COLUMN,
    CCORE_TASK_EXECUTION_UPDATED_AT_COLUMN,
    CCORE_TASK_EXECUTION_VALIDATION_SNAPSHOT_COLUMN,
    CCORE_TASK_EXECUTIONS_TABLE_NAME,
)


class CCoreTaskExecutionRepository:
    def __init__(self, db_manager: DatabaseConnectionProviderProtocol):
        self.db_manager = db_manager

    def _map_row_to_execution(self, row) -> CCoreTaskExecution:
        return CCoreTaskExecution(
            execution_id=str(row[0]),
            task_id=str(row[1]),
            execution_status_id=row[2],
            status_label=row[3],
            provider_profile=row[4],
            execution_mode=row[5],
            requested_by=row[6],
            input_payload=row[7],
            configuration_snapshot=row[8],
            validation_snapshot=row[9],
            execution_report=row[10],
            error_details=row[11],
            started_at=row[12].isoformat() if row[12] is not None else None,
            completed_at=row[13].isoformat() if row[13] is not None else None,
            failed_at=row[14].isoformat() if row[14] is not None else None,
            created_at=row[15].isoformat() if row[15] is not None else None,
            updated_at=row[16].isoformat() if row[16] is not None else None,
        )

    def _execution_select_columns(self) -> str:
        return f"""
            execution.{CCORE_TASK_EXECUTION_ID_COLUMN},
            execution.{CCORE_TASK_EXECUTION_TASK_ID_COLUMN},
            execution.{CCORE_TASK_EXECUTION_STATUS_ID_COLUMN},
            status.{CCORE_TASK_EXECUTION_STATUS_LABEL_COLUMN},
            execution.{CCORE_TASK_EXECUTION_PROVIDER_PROFILE_COLUMN},
            execution.{CCORE_TASK_EXECUTION_MODE_COLUMN},
            execution.{CCORE_TASK_EXECUTION_REQUESTED_BY_COLUMN},
            execution.{CCORE_TASK_EXECUTION_INPUT_PAYLOAD_COLUMN},
            execution.{CCORE_TASK_EXECUTION_CONFIGURATION_SNAPSHOT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_VALIDATION_SNAPSHOT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_REPORT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_ERROR_DETAILS_COLUMN},
            execution.{CCORE_TASK_EXECUTION_STARTED_AT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_COMPLETED_AT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_FAILED_AT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_CREATED_AT_COLUMN},
            execution.{CCORE_TASK_EXECUTION_UPDATED_AT_COLUMN}
        """

    def create_execution(self, execution: CCoreTaskExecution) -> CCoreTaskExecution:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {CCORE_TASK_EXECUTIONS_TABLE_NAME} (
                        {CCORE_TASK_EXECUTION_TASK_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_STATUS_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_PROVIDER_PROFILE_COLUMN},
                        {CCORE_TASK_EXECUTION_MODE_COLUMN},
                        {CCORE_TASK_EXECUTION_REQUESTED_BY_COLUMN},
                        {CCORE_TASK_EXECUTION_INPUT_PAYLOAD_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_SNAPSHOT_COLUMN},
                        {CCORE_TASK_EXECUTION_VALIDATION_SNAPSHOT_COLUMN},
                        {CCORE_TASK_EXECUTION_REPORT_COLUMN},
                        {CCORE_TASK_EXECUTION_ERROR_DETAILS_COLUMN},
                        {CCORE_TASK_EXECUTION_STARTED_AT_COLUMN},
                        {CCORE_TASK_EXECUTION_COMPLETED_AT_COLUMN},
                        {CCORE_TASK_EXECUTION_FAILED_AT_COLUMN}
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    RETURNING {CCORE_TASK_EXECUTION_ID_COLUMN}
                    """,
                    (
                        execution.task_id,
                        execution.execution_status_id,
                        execution.provider_profile,
                        execution.execution_mode,
                        execution.requested_by,
                        Json(execution.input_payload or {}),
                        Json(execution.configuration_snapshot or {}),
                        Json(execution.validation_snapshot or {}),
                        Json(execution.execution_report or {}),
                        Json(execution.error_details) if execution.error_details is not None else None,
                        execution.started_at,
                        execution.completed_at,
                        execution.failed_at,
                    ),
                )
                execution_id = str(cursor.fetchone()[0])

            connection.commit()

        created_execution = self.find_by_execution_id(execution_id)

        if created_execution is None:
            raise RuntimeError(
                f"Created CCore task execution could not be read: {execution_id}"
            )

        return created_execution

    def update_execution_status(
        self,
        execution_id: str,
        execution_status_id: int,
    ) -> CCoreTaskExecution | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {CCORE_TASK_EXECUTIONS_TABLE_NAME}
                    SET
                        {CCORE_TASK_EXECUTION_STATUS_ID_COLUMN} = %s,
                        {CCORE_TASK_EXECUTION_UPDATED_AT_COLUMN} = CURRENT_TIMESTAMP
                    WHERE {CCORE_TASK_EXECUTION_ID_COLUMN} = %s
                    RETURNING {CCORE_TASK_EXECUTION_ID_COLUMN}
                    """,
                    (
                        execution_status_id,
                        execution_id,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        if row is None:
            return None

        return self.find_by_execution_id(str(row[0]))

    def update_execution_snapshots(
        self,
        execution_id: str,
        configuration_snapshot: dict,
        validation_snapshot: dict,
    ) -> CCoreTaskExecution | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {CCORE_TASK_EXECUTIONS_TABLE_NAME}
                    SET
                        {CCORE_TASK_EXECUTION_CONFIGURATION_SNAPSHOT_COLUMN} = %s,
                        {CCORE_TASK_EXECUTION_VALIDATION_SNAPSHOT_COLUMN} = %s,
                        {CCORE_TASK_EXECUTION_UPDATED_AT_COLUMN} = CURRENT_TIMESTAMP
                    WHERE {CCORE_TASK_EXECUTION_ID_COLUMN} = %s
                    RETURNING {CCORE_TASK_EXECUTION_ID_COLUMN}
                    """,
                    (
                        Json(configuration_snapshot or {}),
                        Json(validation_snapshot or {}),
                        execution_id,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        if row is None:
            return None

        return self.find_by_execution_id(str(row[0]))

    def update_execution_result(
        self,
        execution_id: str,
        execution_status_id: int,
        execution_report: dict,
        error_details: dict | None = None,
    ) -> CCoreTaskExecution | None:
        completed_at_expression = (
            "CURRENT_TIMESTAMP"
            if execution_status_id == CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED
            else "NULL"
        )
        failed_at_expression = (
            "CURRENT_TIMESTAMP"
            if execution_status_id == CCORE_TASK_EXECUTION_STATUS_ID_FAILED
            else "NULL"
        )

        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {CCORE_TASK_EXECUTIONS_TABLE_NAME}
                    SET
                        {CCORE_TASK_EXECUTION_STATUS_ID_COLUMN} = %s,
                        {CCORE_TASK_EXECUTION_REPORT_COLUMN} = %s,
                        {CCORE_TASK_EXECUTION_ERROR_DETAILS_COLUMN} = %s,
                        {CCORE_TASK_EXECUTION_COMPLETED_AT_COLUMN} = {completed_at_expression},
                        {CCORE_TASK_EXECUTION_FAILED_AT_COLUMN} = {failed_at_expression},
                        {CCORE_TASK_EXECUTION_UPDATED_AT_COLUMN} = CURRENT_TIMESTAMP
                    WHERE {CCORE_TASK_EXECUTION_ID_COLUMN} = %s
                    RETURNING {CCORE_TASK_EXECUTION_ID_COLUMN}
                    """,
                    (
                        execution_status_id,
                        Json(execution_report or {}),
                        Json(error_details) if error_details is not None else None,
                        execution_id,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        if row is None:
            return None

        return self.find_by_execution_id(str(row[0]))

    def find_by_execution_id(self, execution_id: str) -> CCoreTaskExecution | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._execution_select_columns()}
                    FROM {CCORE_TASK_EXECUTIONS_TABLE_NAME} execution
                    INNER JOIN {CCORE_TASK_EXECUTION_STATUSES_TABLE_NAME} status
                        ON status.{CCORE_TASK_EXECUTION_STATUS_ID_COLUMN}
                        = execution.{CCORE_TASK_EXECUTION_STATUS_ID_COLUMN}
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

    def _find_by_task_id(
        self,
        task_id: str,
        limit: int | None,
    ) -> list[CCoreTaskExecution]:
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
                        ON status.{CCORE_TASK_EXECUTION_STATUS_ID_COLUMN}
                        = execution.{CCORE_TASK_EXECUTION_STATUS_ID_COLUMN}
                    WHERE execution.{CCORE_TASK_EXECUTION_TASK_ID_COLUMN} = %s
                    ORDER BY execution.{CCORE_TASK_EXECUTION_CREATED_AT_COLUMN} DESC
                    {limit_clause}
                    """,
                    tuple(parameters),
                )
                rows = cursor.fetchall()

        return [self._map_row_to_execution(row) for row in rows]
