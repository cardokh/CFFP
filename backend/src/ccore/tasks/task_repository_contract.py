"""
CCore task repository contracts.

Responsibilities:
- Define replaceable persistence contracts for CCore task services.
- Keep services dependent on abstractions instead of concrete PostgreSQL repositories.
- Support future SQLite, MySQL, test-double, or remote repository implementations.
"""

from typing import Protocol

from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_status import CCoreTaskStatus


class CCoreTaskRepositoryProtocol(Protocol):
    def find_all_tasks(self) -> list[CCoreTask]: ...

    def find_by_id(self, task_id: str) -> CCoreTask | None: ...

    def create_task(self, task: CCoreTask) -> CCoreTask: ...

    def update_task(self, task: CCoreTask) -> CCoreTask | None: ...

    def update_task_status(
        self, task_id: str, status_code: str
    ) -> CCoreTask | None: ...

    def delete_task(self, task_id: str) -> bool: ...


class CCoreTaskStatusRepositoryProtocol(Protocol):
    def find_all_statuses(self) -> list[CCoreTaskStatus]: ...

    def status_exists(self, status_code: str) -> bool: ...
