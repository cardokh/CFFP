"""
CCore task domain object.

Responsibilities:
- Represent rows from the ccore_tasks PostgreSQL table as domain objects.
- Keep database row structure separate from API response structure.
- Carry standard CRUD metadata used by CCore vertical-slice blueprints.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CCoreTask:
    task_id: str | None
    task_name: str
    status_code: str
    status_label: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
