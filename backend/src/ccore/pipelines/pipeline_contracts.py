"""CCore pipeline request contracts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.src.ccore.pipelines.pipeline_constants import (
    CCORE_PIPELINE_API_FIELD_PIPELINE_DESCRIPTION,
    CCORE_PIPELINE_API_FIELD_PIPELINE_NAME,
    CCORE_PIPELINE_API_FIELD_PIPELINE_STATUS_ID,
)


@dataclass(frozen=True)
class CreateCCorePipelineRequest:
    pipeline_name: str
    pipeline_description: str | None
    pipeline_status_id: int


@dataclass(frozen=True)
class UpdateCCorePipelineRequest:
    pipeline_id: str
    pipeline_name: str
    pipeline_description: str | None
    pipeline_status_id: int


class CCorePipelineRequestParser:
    def parse_create_request(self, request_data: dict[str, Any]) -> CreateCCorePipelineRequest:
        return CreateCCorePipelineRequest(
            pipeline_name=str(request_data.get(CCORE_PIPELINE_API_FIELD_PIPELINE_NAME, "")).strip(),
            pipeline_description=self._optional_string(request_data.get(CCORE_PIPELINE_API_FIELD_PIPELINE_DESCRIPTION)),
            pipeline_status_id=self._required_int(request_data.get(CCORE_PIPELINE_API_FIELD_PIPELINE_STATUS_ID)),
        )

    def parse_update_request(self, pipeline_id: str, request_data: dict[str, Any]) -> UpdateCCorePipelineRequest:
        return UpdateCCorePipelineRequest(
            pipeline_id=pipeline_id,
            pipeline_name=str(request_data.get(CCORE_PIPELINE_API_FIELD_PIPELINE_NAME, "")).strip(),
            pipeline_description=self._optional_string(request_data.get(CCORE_PIPELINE_API_FIELD_PIPELINE_DESCRIPTION)),
            pipeline_status_id=self._required_int(request_data.get(CCORE_PIPELINE_API_FIELD_PIPELINE_STATUS_ID)),
        )

    def _optional_string(self, value: Any) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized if normalized else None

    def _required_int(self, value: Any) -> int:
        if value is None or str(value).strip() == "":
            raise ValueError("A required integer field is missing.")
        try:
            return int(value)
        except (TypeError, ValueError) as error:
            raise ValueError("A required integer field is invalid.") from error
