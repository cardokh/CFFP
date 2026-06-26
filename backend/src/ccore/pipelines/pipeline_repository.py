"""CCore pipeline PostgreSQL repository."""
from __future__ import annotations

from backend.src.ccore.infrastructure.database_contracts import DatabaseConnectionProviderProtocol
from backend.src.ccore.pipelines.pipeline import CCorePipeline, CCorePipelineStatus
from backend.src.ccore.pipelines.pipeline_constants import (
    CCORE_PIPELINE_CREATED_AT_COLUMN,
    CCORE_PIPELINE_DESCRIPTION_COLUMN,
    CCORE_PIPELINE_ID_COLUMN,
    CCORE_PIPELINE_NAME_COLUMN,
    CCORE_PIPELINE_STATUS_ID_COLUMN,
    CCORE_PIPELINE_STATUS_LABEL_COLUMN,
    CCORE_PIPELINE_STATUS_SORT_ORDER_COLUMN,
    CCORE_PIPELINE_STATUSES_TABLE_NAME,
    CCORE_PIPELINE_UPDATED_AT_COLUMN,
    CCORE_PIPELINES_TABLE_NAME,
)


class CCorePipelineRepository:
    def __init__(self, db_manager: DatabaseConnectionProviderProtocol):
        self.db_manager = db_manager

    def _map_row_to_pipeline(self, row) -> CCorePipeline:
        return CCorePipeline(
            pipeline_id=str(row[0]),
            pipeline_name=row[1],
            pipeline_description=row[2],
            pipeline_status_id=row[3],
            pipeline_status_label=row[4],
            created_at=row[5].isoformat() if row[5] is not None else None,
            updated_at=row[6].isoformat() if row[6] is not None else None,
        )

    def _pipeline_select_columns(self) -> str:
        return f"""
            pipeline.{CCORE_PIPELINE_ID_COLUMN},
            pipeline.{CCORE_PIPELINE_NAME_COLUMN},
            pipeline.{CCORE_PIPELINE_DESCRIPTION_COLUMN},
            pipeline.{CCORE_PIPELINE_STATUS_ID_COLUMN},
            pipeline_status.{CCORE_PIPELINE_STATUS_LABEL_COLUMN},
            pipeline.{CCORE_PIPELINE_CREATED_AT_COLUMN},
            pipeline.{CCORE_PIPELINE_UPDATED_AT_COLUMN}
        """

    def find_all_pipelines(self) -> list[CCorePipeline]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._pipeline_select_columns()}
                    FROM {CCORE_PIPELINES_TABLE_NAME} pipeline
                    INNER JOIN {CCORE_PIPELINE_STATUSES_TABLE_NAME} pipeline_status
                        ON pipeline_status.{CCORE_PIPELINE_STATUS_ID_COLUMN} = pipeline.{CCORE_PIPELINE_STATUS_ID_COLUMN}
                    ORDER BY pipeline.{CCORE_PIPELINE_CREATED_AT_COLUMN} DESC, pipeline.{CCORE_PIPELINE_NAME_COLUMN} ASC
                    """
                )
                rows = cursor.fetchall()
        return [self._map_row_to_pipeline(row) for row in rows]

    def find_by_id(self, pipeline_id: str) -> CCorePipeline | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._pipeline_select_columns()}
                    FROM {CCORE_PIPELINES_TABLE_NAME} pipeline
                    INNER JOIN {CCORE_PIPELINE_STATUSES_TABLE_NAME} pipeline_status
                        ON pipeline_status.{CCORE_PIPELINE_STATUS_ID_COLUMN} = pipeline.{CCORE_PIPELINE_STATUS_ID_COLUMN}
                    WHERE pipeline.{CCORE_PIPELINE_ID_COLUMN} = %s
                    """,
                    (pipeline_id,),
                )
                row = cursor.fetchone()
        return None if row is None else self._map_row_to_pipeline(row)

    def create_pipeline(self, pipeline: CCorePipeline) -> CCorePipeline:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {CCORE_PIPELINES_TABLE_NAME} (
                        {CCORE_PIPELINE_ID_COLUMN},
                        {CCORE_PIPELINE_NAME_COLUMN},
                        {CCORE_PIPELINE_DESCRIPTION_COLUMN},
                        {CCORE_PIPELINE_STATUS_ID_COLUMN}
                    )
                    VALUES (gen_random_uuid(), %s, %s, %s)
                    RETURNING {CCORE_PIPELINE_ID_COLUMN}
                    """,
                    (pipeline.pipeline_name, pipeline.pipeline_description, pipeline.pipeline_status_id),
                )
                pipeline_id = str(cursor.fetchone()[0])
            connection.commit()
        created_pipeline = self.find_by_id(pipeline_id)
        if created_pipeline is None:
            raise RuntimeError(f"Created CCore pipeline could not be read: {pipeline_id}")
        return created_pipeline

    def update_pipeline(self, pipeline: CCorePipeline) -> CCorePipeline | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {CCORE_PIPELINES_TABLE_NAME}
                    SET
                        {CCORE_PIPELINE_NAME_COLUMN} = %s,
                        {CCORE_PIPELINE_DESCRIPTION_COLUMN} = %s,
                        {CCORE_PIPELINE_STATUS_ID_COLUMN} = %s,
                        {CCORE_PIPELINE_UPDATED_AT_COLUMN} = CURRENT_TIMESTAMP
                    WHERE {CCORE_PIPELINE_ID_COLUMN} = %s
                    RETURNING {CCORE_PIPELINE_ID_COLUMN}
                    """,
                    (pipeline.pipeline_name, pipeline.pipeline_description, pipeline.pipeline_status_id, pipeline.pipeline_id),
                )
                row = cursor.fetchone()
            connection.commit()
        return None if row is None else self.find_by_id(str(row[0]))

    def delete_pipeline(self, pipeline_id: str) -> bool:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {CCORE_PIPELINES_TABLE_NAME}
                    WHERE {CCORE_PIPELINE_ID_COLUMN} = %s
                    """,
                    (pipeline_id,),
                )
                deleted_count = cursor.rowcount
            connection.commit()
        return deleted_count > 0


class CCorePipelineStatusRepository:
    def __init__(self, db_manager: DatabaseConnectionProviderProtocol):
        self.db_manager = db_manager

    def _map_row_to_status(self, row) -> CCorePipelineStatus:
        return CCorePipelineStatus(
            pipeline_status_id=row[0],
            status_label=row[1],
            sort_order=row[2],
        )

    def find_all_statuses(self) -> list[CCorePipelineStatus]:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_PIPELINE_STATUS_ID_COLUMN},
                        {CCORE_PIPELINE_STATUS_LABEL_COLUMN},
                        {CCORE_PIPELINE_STATUS_SORT_ORDER_COLUMN}
                    FROM {CCORE_PIPELINE_STATUSES_TABLE_NAME}
                    ORDER BY {CCORE_PIPELINE_STATUS_SORT_ORDER_COLUMN} ASC, {CCORE_PIPELINE_STATUS_LABEL_COLUMN} ASC
                    """
                )
                rows = cursor.fetchall()
        return [self._map_row_to_status(row) for row in rows]

    def find_status_by_id(self, pipeline_status_id: int) -> CCorePipelineStatus | None:
        with self.db_manager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {CCORE_PIPELINE_STATUS_ID_COLUMN},
                        {CCORE_PIPELINE_STATUS_LABEL_COLUMN},
                        {CCORE_PIPELINE_STATUS_SORT_ORDER_COLUMN}
                    FROM {CCORE_PIPELINE_STATUSES_TABLE_NAME}
                    WHERE {CCORE_PIPELINE_STATUS_ID_COLUMN} = %s
                    """,
                    (pipeline_status_id,),
                )
                row = cursor.fetchone()
        return None if row is None else self._map_row_to_status(row)
