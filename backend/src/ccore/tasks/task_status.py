"""
CCore task status domain object.

Responsibilities:
- Represent rows from the ccore_task_statuses reference table.
- Keep task status reference data outside hardcoded frontend/backend option lists.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CCoreTaskStatus:
    status_code: str
    status_label: str
    sort_order: int
