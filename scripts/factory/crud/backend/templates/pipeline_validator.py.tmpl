"""CCore pipeline validation."""
from __future__ import annotations

from backend.src.ccore.pipelines.pipeline import CCorePipeline
from backend.src.ccore.pipelines.pipeline_messages import (
    CCORE_PIPELINE_INVALID_ID_MESSAGE,
    CCORE_PIPELINE_NAME_REQUIRED_MESSAGE,
    CCORE_PIPELINE_STATUS_NOT_FOUND_MESSAGE,
    CCORE_PIPELINE_STATUS_REQUIRED_MESSAGE,
)
from backend.src.ccore.pipelines.pipeline_repository_contract import CCorePipelineStatusRepositoryProtocol


class CCorePipelineValidator:
    def __init__(self, status_repository: CCorePipelineStatusRepositoryProtocol):
        self.status_repository = status_repository

    def validate_pipeline_id(self, pipeline_id: str | None) -> None:
        if pipeline_id is None or not str(pipeline_id).strip():
            raise ValueError(CCORE_PIPELINE_INVALID_ID_MESSAGE)

    def validate_create(self, pipeline: CCorePipeline) -> None:
        self._validate_common_fields(pipeline)

    def validate_update(self, pipeline: CCorePipeline) -> None:
        self.validate_pipeline_id(pipeline.pipeline_id)
        self._validate_common_fields(pipeline)

    def _validate_common_fields(self, pipeline: CCorePipeline) -> None:
        if not pipeline.pipeline_name.strip():
            raise ValueError(CCORE_PIPELINE_NAME_REQUIRED_MESSAGE)
        if pipeline.pipeline_status_id is None:
            raise ValueError(CCORE_PIPELINE_STATUS_REQUIRED_MESSAGE)
        if self.status_repository.find_status_by_id(pipeline.pipeline_status_id) is None:
            raise ValueError(CCORE_PIPELINE_STATUS_NOT_FOUND_MESSAGE)
