"""
CCore task domain object.

Responsibilities:
- Represent rows from the ccore_tasks PostgreSQL table as domain objects.
- Keep database row structure separate from API response structure.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CCoreTask:
    task_id: str | None
    task_name: str
    status: str
    created_at: str | None = None
