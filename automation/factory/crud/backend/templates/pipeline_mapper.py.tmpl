"""CCore pipeline mapper."""
from __future__ import annotations

from backend.src.ccore.pipelines.pipeline import CCorePipeline, CCorePipelineStatus
from backend.src.ccore.pipelines.pipeline_constants import (
    CCORE_PIPELINE_API_FIELD_CREATED_AT,
    CCORE_PIPELINE_API_FIELD_PIPELINE_DESCRIPTION,
    CCORE_PIPELINE_API_FIELD_PIPELINE_ID,
    CCORE_PIPELINE_API_FIELD_PIPELINE_NAME,
    CCORE_PIPELINE_API_FIELD_PIPELINE_STATUS_ID,
    CCORE_PIPELINE_API_FIELD_PIPELINE_STATUS_LABEL,
    CCORE_PIPELINE_API_FIELD_UPDATED_AT,
    CCORE_PIPELINE_STATUS_API_FIELD_ID,
    CCORE_PIPELINE_STATUS_API_FIELD_LABEL,
    CCORE_PIPELINE_STATUS_API_FIELD_SORT_ORDER,
)
from backend.src.ccore.pipelines.pipeline_contracts import (
    CreateCCorePipelineRequest,
    UpdateCCorePipelineRequest,
)


class CCorePipelineMapper:
    def create_request_to_domain(self, request: CreateCCorePipelineRequest) -> CCorePipeline:
        return CCorePipeline(
            pipeline_id=None,
            pipeline_name=request.pipeline_name,
            pipeline_description=request.pipeline_description,
            pipeline_status_id=request.pipeline_status_id,
        )

    def update_request_to_domain(self, request: UpdateCCorePipelineRequest) -> CCorePipeline:
        return CCorePipeline(
            pipeline_id=request.pipeline_id,
            pipeline_name=request.pipeline_name,
            pipeline_description=request.pipeline_description,
            pipeline_status_id=request.pipeline_status_id,
        )

    def domain_to_response(self, pipeline: CCorePipeline) -> dict[str, object]:
        return {
            CCORE_PIPELINE_API_FIELD_PIPELINE_ID: pipeline.pipeline_id,
            CCORE_PIPELINE_API_FIELD_PIPELINE_NAME: pipeline.pipeline_name,
            CCORE_PIPELINE_API_FIELD_PIPELINE_DESCRIPTION: pipeline.pipeline_description,
            CCORE_PIPELINE_API_FIELD_PIPELINE_STATUS_ID: pipeline.pipeline_status_id,
            CCORE_PIPELINE_API_FIELD_PIPELINE_STATUS_LABEL: pipeline.pipeline_status_label,
            CCORE_PIPELINE_API_FIELD_CREATED_AT: pipeline.created_at,
            CCORE_PIPELINE_API_FIELD_UPDATED_AT: pipeline.updated_at,
        }

    def domains_to_response(self, pipelines: list[CCorePipeline]) -> list[dict[str, object]]:
        return [self.domain_to_response(pipeline) for pipeline in pipelines]

    def status_to_response(self, status: CCorePipelineStatus) -> dict[str, object]:
        return {
            CCORE_PIPELINE_STATUS_API_FIELD_ID: status.pipeline_status_id,
            CCORE_PIPELINE_STATUS_API_FIELD_LABEL: status.status_label,
            CCORE_PIPELINE_STATUS_API_FIELD_SORT_ORDER: status.sort_order,
        }

    def statuses_to_response(self, statuses: list[CCorePipelineStatus]) -> list[dict[str, object]]:
        return [self.status_to_response(status) for status in statuses]
