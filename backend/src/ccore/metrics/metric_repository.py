"""
CCore metric PostgreSQL repository.

Responsibilities:
- Execute ccore_metrics CRUD queries.
- Map PostgreSQL rows to CCore metric domain objects.
- Keep SQL access isolated from routes and services.
"""

from backend.src.ccore.infrastructure.database_contracts import (
    DatabaseConnectionProviderProtocol,
)
from backend.src.ccore.metrics.metric import CCoreMetric
from backend.src.ccore.metrics.metric_constants import (
    CCORE_METRIC_CREATED_AT_COLUMN,
    CCORE_METRIC_ID_COLUMN,
    CCORE_METRIC_KEY_COLUMN,
    CCORE_METRIC_NAME_COLUMN,
    CCORE_METRIC_TYPE_ID_COLUMN,
    CCORE_METRIC_TYPE_LABEL_COLUMN,
    CCORE_METRIC_TYPE_SORT_ORDER_COLUMN,
    CCORE_METRIC_TYPES_TABLE_NAME,
    CCORE_METRICS_TABLE_NAME,
)
from backend.src.ccore.metrics.metric_type import CCoreMetricType


class CCoreMetricRepository:
    def __init__(self, db_manager: DatabaseConnectionProviderProtocol):
        self.db_manager = db_manager

    def _map_row_to_metric(self, row) -> CCoreMetric:
        return CCoreMetric(
            metric_id=str(row[0]),
            metric_name=row[1],
            metric_key=row[2],
            metric_type_id=row[3],
            metric_type_label=row[4],
            created_at=row[5].isoformat() if row[5] is not None else None,
        )

    def _metric_select_columns(self) -> str:
        return f"""
            metric.{CCORE_METRIC_ID_COLUMN},
            metric.{CCORE_METRIC_NAME_COLUMN},
            metric.{CCORE_METRIC_KEY_COLUMN},
            metric.{CCORE_METRIC_TYPE_ID_COLUMN},
            metric_type.{CCORE_METRIC_TYPE_LABEL_COLUMN},
            metric.{CCORE_METRIC_CREATED_AT_COLUMN}
        """

    def find_all_metrics(self) -> list[CCoreMetric]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._metric_select_columns()}
                    FROM {CCORE_METRICS_TABLE_NAME} metric
                    INNER JOIN {CCORE_METRIC_TYPES_TABLE_NAME} metric_type
                        ON metric_type.{CCORE_METRIC_TYPE_ID_COLUMN} = metric.{CCORE_METRIC_TYPE_ID_COLUMN}
                    ORDER BY metric.{CCORE_METRIC_CREATED_AT_COLUMN} DESC, metric.{CCORE_METRIC_NAME_COLUMN} ASC
                    """
                )

                rows = cursor.fetchall()

        return [self._map_row_to_metric(row) for row in rows]

    def find_by_id(self, metric_id: str) -> CCoreMetric | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._metric_select_columns()}
                    FROM {CCORE_METRICS_TABLE_NAME} metric
                    INNER JOIN {CCORE_METRIC_TYPES_TABLE_NAME} metric_type
                        ON metric_type.{CCORE_METRIC_TYPE_ID_COLUMN} = metric.{CCORE_METRIC_TYPE_ID_COLUMN}
                    WHERE metric.{CCORE_METRIC_ID_COLUMN} = %s
                    """,
                    (metric_id,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return self._map_row_to_metric(row)

    def create_metric(self, metric: CCoreMetric) -> CCoreMetric:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {CCORE_METRICS_TABLE_NAME} (
                        {CCORE_METRIC_ID_COLUMN},
                        {CCORE_METRIC_NAME_COLUMN},
                        {CCORE_METRIC_KEY_COLUMN},
                        {CCORE_METRIC_TYPE_ID_COLUMN}
                    )
                    VALUES (
                        gen_random_uuid(),
                        %s,
                        %s,
                        %s
                    )
                    RETURNING {CCORE_METRIC_ID_COLUMN}
                    """,
                    (
                        metric.metric_name,
                        metric.metric_key,
                        metric.metric_type_id,
                    ),
                )

                metric_id = str(cursor.fetchone()[0])

            connection.commit()

        created_metric = self.find_by_id(metric_id)

        if created_metric is None:
            raise RuntimeError(f"Created CCore metric could not be read: {metric_id}")

        return created_metric

    def update_metric(self, metric: CCoreMetric) -> CCoreMetric | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {CCORE_METRICS_TABLE_NAME}
                    SET
                        {CCORE_METRIC_NAME_COLUMN} = %s,
                        {CCORE_METRIC_KEY_COLUMN} = %s,
                        {CCORE_METRIC_TYPE_ID_COLUMN} = %s
                    WHERE {CCORE_METRIC_ID_COLUMN} = %s
                    RETURNING {CCORE_METRIC_ID_COLUMN}
                    """,
                    (
                        metric.metric_name,
                        metric.metric_key,
                        metric.metric_type_id,
                        metric.metric_id,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

        if row is None:
            return None

        return self.find_by_id(str(row[0]))

    def delete_metric(self, metric_id: str) -> bool:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {CCORE_METRICS_TABLE_NAME}
                    WHERE {CCORE_METRIC_ID_COLUMN} = %s
                    """,
                    (metric_id,),
                )

                deleted_count = cursor.rowcount

            connection.commit()

        return deleted_count > 0


class CCoreMetricTypeRepository:
    def __init__(self, db_manager: DatabaseConnectionProviderProtocol):
        self.db_manager = db_manager

    def _map_row_to_type(self, row) -> CCoreMetricType:
        return CCoreMetricType(
            metric_type_id=row[0],
            metric_type_label=row[1],
            sort_order=row[2],
        )

    def find_all_types(self) -> list[CCoreMetricType]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_METRIC_TYPE_ID_COLUMN},
                        {CCORE_METRIC_TYPE_LABEL_COLUMN},
                        {CCORE_METRIC_TYPE_SORT_ORDER_COLUMN}
                    FROM {CCORE_METRIC_TYPES_TABLE_NAME}
                    ORDER BY {CCORE_METRIC_TYPE_SORT_ORDER_COLUMN} ASC, {CCORE_METRIC_TYPE_LABEL_COLUMN} ASC
                    """
                )

                rows = cursor.fetchall()

        return [self._map_row_to_type(row) for row in rows]

    def type_exists(self, metric_type_id: int) -> bool:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT 1
                    FROM {CCORE_METRIC_TYPES_TABLE_NAME}
                    WHERE {CCORE_METRIC_TYPE_ID_COLUMN} = %s
                    """,
                    (metric_type_id,),
                )

                return cursor.fetchone() is not None
