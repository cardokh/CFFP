"""
CCore task execution PostgreSQL repository.

Responsibilities:
- Persist task execution records and reports.
- Read latest execution and execution history for CCore task details views.
- Read execution provider, implementer type, target, and configuration metadata.
- Keep SQL details isolated from services and route handlers.
"""

from psycopg2.extras import Json

from backend.src.ccore.infrastructure.database_contracts import (
    DatabaseConnectionProviderProtocol,
)
from backend.src.ccore.tasks.task_execution import (
    CCoreExecutionConfiguration,
    CCoreExecutionConfigurationElement,
    CCoreExecutionImplementerType,
    CCoreExecutionProvider,
    CCoreExecutionTarget,
    CCoreTaskExecution,
)
from backend.src.ccore.tasks.task_execution_constants import (
    CCORE_TASK_EXECUTION_COMPLETED_AT_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_DESCRIPTION_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_ID_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_NAME_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_SORT_ORDER_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_VALUE_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENTS_TABLE_NAME,
    CCORE_TASK_EXECUTION_CONFIGURATION_ID_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_LABEL_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_SNAPSHOT_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATION_SORT_ORDER_COLUMN,
    CCORE_TASK_EXECUTION_CONFIGURATIONS_TABLE_NAME,
    CCORE_TASK_EXECUTION_CREATED_AT_COLUMN,
    CCORE_TASK_EXECUTION_ERROR_DETAILS_COLUMN,
    CCORE_TASK_EXECUTION_FAILED_AT_COLUMN,
    CCORE_TASK_EXECUTION_ID_COLUMN,
    CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_ID_COLUMN,
    CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_LABEL_COLUMN,
    CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_SORT_ORDER_COLUMN,
    CCORE_TASK_EXECUTION_IMPLEMENTER_TYPES_TABLE_NAME,
    CCORE_TASK_EXECUTION_INPUT_PAYLOAD_COLUMN,
    CCORE_TASK_EXECUTION_PROVIDER_ID_COLUMN,
    CCORE_TASK_EXECUTION_PROVIDER_LABEL_COLUMN,
    CCORE_TASK_EXECUTION_PROVIDER_SORT_ORDER_COLUMN,
    CCORE_TASK_EXECUTION_PROVIDERS_TABLE_NAME,
    CCORE_TASK_EXECUTION_REPORT_COLUMN,
    CCORE_TASK_EXECUTION_REQUESTED_BY_COLUMN,
    CCORE_TASK_EXECUTION_STARTED_AT_COLUMN,
    CCORE_TASK_EXECUTION_STATUSES_TABLE_NAME,
    CCORE_TASK_EXECUTION_STATUS_ID_COLUMN,
    CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED,
    CCORE_TASK_EXECUTION_STATUS_ID_FAILED,
    CCORE_TASK_EXECUTION_STATUS_LABEL_COLUMN,
    CCORE_TASK_EXECUTION_TARGET_ID_COLUMN,
    CCORE_TASK_EXECUTION_TARGET_LABEL_COLUMN,
    CCORE_TASK_EXECUTION_TARGET_REFERENCE_COLUMN,
    CCORE_TASK_EXECUTION_TARGET_SORT_ORDER_COLUMN,
    CCORE_TASK_EXECUTION_TARGETS_TABLE_NAME,
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
            execution_provider_id=row[4],
            provider_label=row[5],
            execution_implementer_type_id=row[6],
            implementer_type_label=row[7],
            execution_target_id=row[8],
            target_label=row[9],
            target_reference=row[10],
            execution_configuration_id=row[11],
            configuration_label=row[12],
            configuration_description=row[13],
            requested_by=row[14],
            input_payload=row[15],
            configuration_snapshot=row[16],
            validation_snapshot=row[17],
            execution_report=row[18],
            error_details=row[19],
            started_at=row[20].isoformat() if row[20] is not None else None,
            completed_at=row[21].isoformat() if row[21] is not None else None,
            failed_at=row[22].isoformat() if row[22] is not None else None,
            created_at=row[23].isoformat() if row[23] is not None else None,
            updated_at=row[24].isoformat() if row[24] is not None else None,
        )

    def _execution_select_columns(self) -> str:
        return f"""
            execution.{CCORE_TASK_EXECUTION_ID_COLUMN},
            execution.{CCORE_TASK_EXECUTION_TASK_ID_COLUMN},
            execution.{CCORE_TASK_EXECUTION_STATUS_ID_COLUMN},
            status.{CCORE_TASK_EXECUTION_STATUS_LABEL_COLUMN},
            execution.{CCORE_TASK_EXECUTION_PROVIDER_ID_COLUMN},
            provider.{CCORE_TASK_EXECUTION_PROVIDER_LABEL_COLUMN},
            execution.{CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_ID_COLUMN},
            implementer_type.{CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_LABEL_COLUMN},
            execution.{CCORE_TASK_EXECUTION_TARGET_ID_COLUMN},
            target.{CCORE_TASK_EXECUTION_TARGET_LABEL_COLUMN},
            target.{CCORE_TASK_EXECUTION_TARGET_REFERENCE_COLUMN},
            execution.{CCORE_TASK_EXECUTION_CONFIGURATION_ID_COLUMN},
            configuration.{CCORE_TASK_EXECUTION_CONFIGURATION_LABEL_COLUMN},
            configuration.{CCORE_TASK_EXECUTION_CONFIGURATION_DESCRIPTION_COLUMN},
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

    def _execution_joins(self) -> str:
        return f"""
            INNER JOIN {CCORE_TASK_EXECUTION_STATUSES_TABLE_NAME} status
                ON status.{CCORE_TASK_EXECUTION_STATUS_ID_COLUMN}
                = execution.{CCORE_TASK_EXECUTION_STATUS_ID_COLUMN}
            INNER JOIN {CCORE_TASK_EXECUTION_PROVIDERS_TABLE_NAME} provider
                ON provider.{CCORE_TASK_EXECUTION_PROVIDER_ID_COLUMN}
                = execution.{CCORE_TASK_EXECUTION_PROVIDER_ID_COLUMN}
            INNER JOIN {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPES_TABLE_NAME} implementer_type
                ON implementer_type.{CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_ID_COLUMN}
                = execution.{CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_ID_COLUMN}
            INNER JOIN {CCORE_TASK_EXECUTION_TARGETS_TABLE_NAME} target
                ON target.{CCORE_TASK_EXECUTION_TARGET_ID_COLUMN}
                = execution.{CCORE_TASK_EXECUTION_TARGET_ID_COLUMN}
            INNER JOIN {CCORE_TASK_EXECUTION_CONFIGURATIONS_TABLE_NAME} configuration
                ON configuration.{CCORE_TASK_EXECUTION_CONFIGURATION_ID_COLUMN}
                = execution.{CCORE_TASK_EXECUTION_CONFIGURATION_ID_COLUMN}
        """

    def create_execution(self, execution: CCoreTaskExecution) -> CCoreTaskExecution:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {CCORE_TASK_EXECUTIONS_TABLE_NAME} (
                        {CCORE_TASK_EXECUTION_TASK_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_STATUS_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_PROVIDER_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_TARGET_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_ID_COLUMN},
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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING {CCORE_TASK_EXECUTION_ID_COLUMN}
                    """,
                    (
                        execution.task_id,
                        execution.execution_status_id,
                        execution.execution_provider_id,
                        execution.execution_implementer_type_id,
                        execution.execution_target_id,
                        execution.execution_configuration_id,
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
            raise RuntimeError(f"Created CCore task execution could not be read: {execution_id}")
        return created_execution

    def update_execution_status(self, execution_id: str, execution_status_id: int) -> CCoreTaskExecution | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {CCORE_TASK_EXECUTIONS_TABLE_NAME}
                    SET
                        {CCORE_TASK_EXECUTION_STATUS_ID_COLUMN} = %s,
                        {CCORE_TASK_EXECUTION_STARTED_AT_COLUMN} = COALESCE({CCORE_TASK_EXECUTION_STARTED_AT_COLUMN}, CURRENT_TIMESTAMP),
                        {CCORE_TASK_EXECUTION_UPDATED_AT_COLUMN} = CURRENT_TIMESTAMP
                    WHERE {CCORE_TASK_EXECUTION_ID_COLUMN} = %s
                    RETURNING {CCORE_TASK_EXECUTION_ID_COLUMN}
                    """,
                    (execution_status_id, execution_id),
                )
                row = cursor.fetchone()
            connection.commit()
        return self.find_by_execution_id(str(row[0])) if row is not None else None

    def update_execution_snapshots(self, execution_id: str, configuration_snapshot: dict, validation_snapshot: dict) -> CCoreTaskExecution | None:
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
                    (Json(configuration_snapshot or {}), Json(validation_snapshot or {}), execution_id),
                )
                row = cursor.fetchone()
            connection.commit()
        return self.find_by_execution_id(str(row[0])) if row is not None else None

    def update_execution_result(self, execution_id: str, execution_status_id: int, execution_report: dict, error_details: dict | None = None) -> CCoreTaskExecution | None:
        completed_at_expression = "CURRENT_TIMESTAMP" if execution_status_id == CCORE_TASK_EXECUTION_STATUS_ID_COMPLETED else "NULL"
        failed_at_expression = "CURRENT_TIMESTAMP" if execution_status_id == CCORE_TASK_EXECUTION_STATUS_ID_FAILED else "NULL"
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
                    (execution_status_id, Json(execution_report or {}), Json(error_details) if error_details is not None else None, execution_id),
                )
                row = cursor.fetchone()
            connection.commit()
        return self.find_by_execution_id(str(row[0])) if row is not None else None

    def find_by_execution_id(self, execution_id: str) -> CCoreTaskExecution | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT {self._execution_select_columns()}
                    FROM {CCORE_TASK_EXECUTIONS_TABLE_NAME} execution
                    {self._execution_joins()}
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
                    SELECT {self._execution_select_columns()}
                    FROM {CCORE_TASK_EXECUTIONS_TABLE_NAME} execution
                    {self._execution_joins()}
                    WHERE execution.{CCORE_TASK_EXECUTION_TASK_ID_COLUMN} = %s
                    ORDER BY execution.{CCORE_TASK_EXECUTION_CREATED_AT_COLUMN} DESC
                    {limit_clause}
                    """,
                    tuple(parameters),
                )
                rows = cursor.fetchall()
        return [self._map_row_to_execution(row) for row in rows]

    def find_all_execution_providers(self) -> list[CCoreExecutionProvider]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_TASK_EXECUTION_PROVIDER_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_PROVIDER_LABEL_COLUMN},
                        {CCORE_TASK_EXECUTION_PROVIDER_SORT_ORDER_COLUMN}
                    FROM {CCORE_TASK_EXECUTION_PROVIDERS_TABLE_NAME}
                    ORDER BY {CCORE_TASK_EXECUTION_PROVIDER_SORT_ORDER_COLUMN}, {CCORE_TASK_EXECUTION_PROVIDER_LABEL_COLUMN}
                    """
                )
                rows = cursor.fetchall()
        return [CCoreExecutionProvider(row[0], row[1], row[2]) for row in rows]

    def find_all_execution_implementer_types(self) -> list[CCoreExecutionImplementerType]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_LABEL_COLUMN},
                        {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_SORT_ORDER_COLUMN}
                    FROM {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPES_TABLE_NAME}
                    ORDER BY {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_SORT_ORDER_COLUMN}, {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_LABEL_COLUMN}
                    """
                )
                rows = cursor.fetchall()
        return [CCoreExecutionImplementerType(row[0], row[1], row[2]) for row in rows]

    def find_all_execution_targets(self) -> list[CCoreExecutionTarget]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_TASK_EXECUTION_TARGET_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_IMPLEMENTER_TYPE_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_TARGET_LABEL_COLUMN},
                        {CCORE_TASK_EXECUTION_TARGET_REFERENCE_COLUMN},
                        {CCORE_TASK_EXECUTION_TARGET_SORT_ORDER_COLUMN}
                    FROM {CCORE_TASK_EXECUTION_TARGETS_TABLE_NAME}
                    ORDER BY {CCORE_TASK_EXECUTION_TARGET_SORT_ORDER_COLUMN}, {CCORE_TASK_EXECUTION_TARGET_LABEL_COLUMN}
                    """
                )
                rows = cursor.fetchall()
        return [CCoreExecutionTarget(row[0], row[1], row[2], row[3], row[4]) for row in rows]

    def find_all_execution_configurations(self) -> list[CCoreExecutionConfiguration]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_TASK_EXECUTION_CONFIGURATION_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_TARGET_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_LABEL_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_DESCRIPTION_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_SORT_ORDER_COLUMN}
                    FROM {CCORE_TASK_EXECUTION_CONFIGURATIONS_TABLE_NAME}
                    ORDER BY {CCORE_TASK_EXECUTION_CONFIGURATION_SORT_ORDER_COLUMN}, {CCORE_TASK_EXECUTION_CONFIGURATION_LABEL_COLUMN}
                    """
                )
                rows = cursor.fetchall()
        return [CCoreExecutionConfiguration(row[0], row[1], row[2], row[3], row[4]) for row in rows]

    def find_execution_configuration_elements_by_configuration_id(self, execution_configuration_id: int) -> list[CCoreExecutionConfigurationElement]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_ID_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_NAME_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_VALUE_COLUMN},
                        {CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_SORT_ORDER_COLUMN}
                    FROM {CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENTS_TABLE_NAME}
                    WHERE {CCORE_TASK_EXECUTION_CONFIGURATION_ID_COLUMN} = %s
                    ORDER BY {CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_SORT_ORDER_COLUMN}, {CCORE_TASK_EXECUTION_CONFIGURATION_ELEMENT_NAME_COLUMN}
                    """,
                    (execution_configuration_id,),
                )
                rows = cursor.fetchall()
        return [CCoreExecutionConfigurationElement(row[0], row[1], row[2], row[3], row[4]) for row in rows]

    def find_execution_provider_by_id(self, execution_provider_id: int) -> CCoreExecutionProvider | None:
        providers = [p for p in self.find_all_execution_providers() if p.execution_provider_id == execution_provider_id]
        return providers[0] if providers else None

    def find_execution_implementer_type_by_id(self, execution_implementer_type_id: int) -> CCoreExecutionImplementerType | None:
        implementer_types = [i for i in self.find_all_execution_implementer_types() if i.execution_implementer_type_id == execution_implementer_type_id]
        return implementer_types[0] if implementer_types else None

    def find_execution_target_by_id(self, execution_target_id: int) -> CCoreExecutionTarget | None:
        targets = [target for target in self.find_all_execution_targets() if target.execution_target_id == execution_target_id]
        return targets[0] if targets else None

    def find_execution_configuration_by_id(self, execution_configuration_id: int) -> CCoreExecutionConfiguration | None:
        configurations = [configuration for configuration in self.find_all_execution_configurations() if configuration.execution_configuration_id == execution_configuration_id]
        return configurations[0] if configurations else None
