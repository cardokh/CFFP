"""
CCore metric repository contracts.

Responsibilities:
- Define replaceable persistence contracts for CCore metric services.
- Keep services dependent on abstractions instead of concrete PostgreSQL repositories.
- Support future SQLite, MySQL, test-double, or remote repository implementations.
"""

from typing import Protocol

from backend.src.ccore.metrics.metric import CCoreMetric
from backend.src.ccore.metrics.metric_type import CCoreMetricType


class CCoreMetricRepositoryProtocol(Protocol):
    def find_all_metrics(self) -> list[CCoreMetric]: ...

    def find_by_id(self, metric_id: str) -> CCoreMetric | None: ...

    def create_metric(self, metric: CCoreMetric) -> CCoreMetric: ...

    def update_metric(self, metric: CCoreMetric) -> CCoreMetric | None: ...

    def delete_metric(self, metric_id: str) -> bool: ...


class CCoreMetricTypeRepositoryProtocol(Protocol):
    def find_all_types(self) -> list[CCoreMetricType]: ...

    def type_exists(self, metric_type_id: int) -> bool: ...
