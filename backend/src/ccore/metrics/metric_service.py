"""
CCore metric application services.

Responsibilities:
- Coordinate CCore metric CRUD use cases.
- Expose metric type reference data for UI/API consumers.
- Delegate validation to CCoreMetricValidator.
- Keep API handlers independent from repository/database details.
"""

from backend.src.ccore.metrics.metric import CCoreMetric
from backend.src.ccore.metrics.metric_repository_contract import (
    CCoreMetricRepositoryProtocol,
    CCoreMetricTypeRepositoryProtocol,
)
from backend.src.ccore.metrics.metric_type import CCoreMetricType
from backend.src.ccore.metrics.metric_validator import CCoreMetricValidator


class CCoreMetricService:
    def __init__(
        self,
        metric_repository: CCoreMetricRepositoryProtocol,
        metric_validator: CCoreMetricValidator,
    ):
        self.metric_repository = metric_repository
        self.metric_validator = metric_validator

    def get_all_metrics(self) -> list[CCoreMetric]:
        return self.metric_repository.find_all_metrics()

    def get_metric_by_id(self, metric_id: str) -> CCoreMetric | None:
        self.metric_validator.validate_metric_id(metric_id)

        return self.metric_repository.find_by_id(metric_id)

    def create_metric(self, metric: CCoreMetric) -> CCoreMetric:
        self.metric_validator.validate_create_metric(metric)

        return self.metric_repository.create_metric(metric)

    def update_metric(self, metric: CCoreMetric) -> CCoreMetric | None:
        self.metric_validator.validate_update_metric(metric)

        return self.metric_repository.update_metric(metric)

    def delete_metric(self, metric_id: str) -> bool:
        self.metric_validator.validate_metric_id(metric_id)

        return self.metric_repository.delete_metric(metric_id)


class CCoreMetricTypeService:
    def __init__(self, type_repository: CCoreMetricTypeRepositoryProtocol):
        self.type_repository = type_repository

    def get_all_types(self) -> list[CCoreMetricType]:
        return self.type_repository.find_all_types()
