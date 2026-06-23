"""
CCore metric mapper.

Responsibilities:
- Convert metric request contracts to domain objects.
- Convert metric domain objects and reference data to API response dictionaries.
- Keep API field names camelCase while preserving database/domain names internally.
- Keep machine identifiers numeric and human-readable labels separate.
"""

from backend.src.ccore.metrics.metric import CCoreMetric
from backend.src.ccore.metrics.metric_constants import (
    CCORE_METRIC_API_FIELD_CREATED_AT,
    CCORE_METRIC_API_FIELD_METRIC_ID,
    CCORE_METRIC_API_FIELD_METRIC_KEY,
    CCORE_METRIC_API_FIELD_METRIC_NAME,
    CCORE_METRIC_API_FIELD_METRIC_TYPE_ID,
    CCORE_METRIC_API_FIELD_METRIC_TYPE_LABEL,
    CCORE_METRIC_TYPE_API_FIELD_ID,
    CCORE_METRIC_TYPE_API_FIELD_LABEL,
    CCORE_METRIC_TYPE_API_FIELD_SORT_ORDER,
    CCORE_METRIC_TYPE_ID_COUNTER,
)
from backend.src.ccore.metrics.metric_contracts import (
    CreateCCoreMetricRequest,
    UpdateCCoreMetricRequest,
)
from backend.src.ccore.metrics.metric_type import CCoreMetricType


class CCoreMetricMapper:
    def create_request_to_domain(
        self,
        request: CreateCCoreMetricRequest,
    ) -> CCoreMetric:
        return CCoreMetric(
            metric_id=None,
            metric_name=request.metric_name,
            metric_key=request.metric_key,
            metric_type_id=request.metric_type_id or CCORE_METRIC_TYPE_ID_COUNTER,
        )

    def update_request_to_domain(
        self,
        request: UpdateCCoreMetricRequest,
    ) -> CCoreMetric:
        return CCoreMetric(
            metric_id=request.metric_id,
            metric_name=request.metric_name,
            metric_key=request.metric_key,
            metric_type_id=request.metric_type_id,
        )

    def domain_to_response(self, metric: CCoreMetric) -> dict:
        return {
            CCORE_METRIC_API_FIELD_METRIC_ID: metric.metric_id,
            CCORE_METRIC_API_FIELD_METRIC_NAME: metric.metric_name,
            CCORE_METRIC_API_FIELD_METRIC_KEY: metric.metric_key,
            CCORE_METRIC_API_FIELD_METRIC_TYPE_ID: metric.metric_type_id,
            CCORE_METRIC_API_FIELD_METRIC_TYPE_LABEL: metric.metric_type_label,
            CCORE_METRIC_API_FIELD_CREATED_AT: metric.created_at,
        }

    def domains_to_response(self, metrics: list[CCoreMetric]) -> list[dict]:
        return [self.domain_to_response(metric) for metric in metrics]

    def type_to_response(self, metric_type: CCoreMetricType) -> dict:
        return {
            CCORE_METRIC_TYPE_API_FIELD_ID: metric_type.metric_type_id,
            CCORE_METRIC_TYPE_API_FIELD_LABEL: metric_type.metric_type_label,
            CCORE_METRIC_TYPE_API_FIELD_SORT_ORDER: metric_type.sort_order,
        }

    def types_to_response(self, metric_types: list[CCoreMetricType]) -> list[dict]:
        return [self.type_to_response(metric_type) for metric_type in metric_types]
