"""
CCore metric type reference-data object.

Responsibilities:
- Represent rows from the ccore_metric_types PostgreSQL lookup table.
- Keep lookup/reference data explicit and reusable across API and validation layers.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CCoreMetricType:
    metric_type_id: int
    metric_type_label: str
    sort_order: int
