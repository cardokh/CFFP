"""
CCore task request contracts.

Responsibilities:
- Represent task create/update request data at the API boundary.
- Keep route handlers independent from domain construction details.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCCoreTaskRequest:
    task_name: str
    status: str | None = None


@dataclass(frozen=True)
class UpdateCCoreTaskRequest:
    task_id: str
    task_name: str
    status: str
