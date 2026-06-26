"""CCore pipeline service layer."""
from __future__ import annotations

from backend.src.ccore.pipelines.pipeline import CCorePipeline, CCorePipelineStatus
from backend.src.ccore.pipelines.pipeline_repository_contract import (
    CCorePipelineRepositoryProtocol,
    CCorePipelineStatusRepositoryProtocol,
)
from backend.src.ccore.pipelines.pipeline_validator import CCorePipelineValidator


class CCorePipelineService:
    def __init__(self, pipeline_repository: CCorePipelineRepositoryProtocol, pipeline_validator: CCorePipelineValidator):
        self.pipeline_repository = pipeline_repository
        self.pipeline_validator = pipeline_validator

    def get_all_pipelines(self) -> list[CCorePipeline]:
        return self.pipeline_repository.find_all_pipelines()

    def get_pipeline_by_id(self, pipeline_id: str) -> CCorePipeline | None:
        self.pipeline_validator.validate_pipeline_id(pipeline_id)
        return self.pipeline_repository.find_by_id(pipeline_id)

    def create_pipeline(self, pipeline: CCorePipeline) -> CCorePipeline:
        self.pipeline_validator.validate_create(pipeline)
        return self.pipeline_repository.create_pipeline(pipeline)

    def update_pipeline(self, pipeline: CCorePipeline) -> CCorePipeline | None:
        self.pipeline_validator.validate_update(pipeline)
        return self.pipeline_repository.update_pipeline(pipeline)

    def delete_pipeline(self, pipeline_id: str) -> bool:
        self.pipeline_validator.validate_pipeline_id(pipeline_id)
        return self.pipeline_repository.delete_pipeline(pipeline_id)


class CCorePipelineStatusService:
    def __init__(self, status_repository: CCorePipelineStatusRepositoryProtocol):
        self.status_repository = status_repository

    def get_all_statuses(self) -> list[CCorePipelineStatus]:
        return self.status_repository.find_all_statuses()
