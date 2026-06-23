"""
CCore metric domain object.

Responsibilities:
- Represent rows from the ccore_metrics PostgreSQL table as domain objects.
- Keep database row structure separate from API response structure.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CCoreMetric:
    metric_id: str | None
    metric_name: str
    metric_key: str
    metric_type_id: int
    metric_type_label: str | None = None
    created_at: str | None = None
