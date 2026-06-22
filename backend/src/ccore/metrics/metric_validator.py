"""
CCore metric validator.

Responsibilities:
- Validate metric domain objects before repository operations.
- Keep validation rules out of route handlers and repositories.
- Validate lookup/reference values through repository contracts.
"""

from backend.src.ccore.metrics.metric import CCoreMetric
from backend.src.ccore.metrics.metric_messages import (
    CCORE_METRIC_INVALID_ID_MESSAGE,
    CCORE_METRIC_KEY_REQUIRED_MESSAGE,
    CCORE_METRIC_NAME_REQUIRED_MESSAGE,
    CCORE_METRIC_TYPE_INVALID_MESSAGE,
    CCORE_METRIC_TYPE_REQUIRED_MESSAGE,
)
from backend.src.ccore.metrics.metric_repository_contract import (
    CCoreMetricTypeRepositoryProtocol,
)


class CCoreMetricValidator:
    def __init__(self, type_repository: CCoreMetricTypeRepositoryProtocol):
        self.type_repository = type_repository

    def validate_metric_id(self, metric_id: str | None) -> None:
        if not metric_id or not str(metric_id).strip():
            raise ValueError(CCORE_METRIC_INVALID_ID_MESSAGE)

    def validate_create_metric(self, metric: CCoreMetric) -> None:
        self._validate_metric_name(metric.metric_name)
        self._validate_metric_key(metric.metric_key)
        self._validate_metric_type(metric.metric_type_code)

    def validate_update_metric(self, metric: CCoreMetric) -> None:
        self.validate_metric_id(metric.metric_id)
        self._validate_metric_name(metric.metric_name)
        self._validate_metric_key(metric.metric_key)
        self._validate_metric_type(metric.metric_type_code)

    def _validate_metric_name(self, metric_name: str | None) -> None:
        if not metric_name or not str(metric_name).strip():
            raise ValueError(CCORE_METRIC_NAME_REQUIRED_MESSAGE)

    def _validate_metric_key(self, metric_key: str | None) -> None:
        if not metric_key or not str(metric_key).strip():
            raise ValueError(CCORE_METRIC_KEY_REQUIRED_MESSAGE)

    def _validate_metric_type(self, metric_type_code: str | None) -> None:
        if not metric_type_code or not str(metric_type_code).strip():
            raise ValueError(CCORE_METRIC_TYPE_REQUIRED_MESSAGE)

        if not self.type_repository.type_exists(str(metric_type_code).strip()):
            raise ValueError(CCORE_METRIC_TYPE_INVALID_MESSAGE)
