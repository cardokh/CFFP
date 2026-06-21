"""Factory task domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FactoryTask:
    """A persisted Automation Factory task."""

    task_id: str
    name: str
    description: str
    status: str
    task_definition_path: str
    priority: int
    payload: str = '{}'
    created_at: str | None = None
    updated_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class FactoryRunnerResult:
    """Summary returned by the Factory task runner."""

    discovered_count: int
    pending_tasks: tuple[FactoryTask, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a serializable runner result."""

        return {
            "discovered_count": self.discovered_count,
            "pending_tasks": [
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "status": task.status,
                    "task_definition_path": task.task_definition_path,
                    "priority": task.priority,
                    "payload": task.payload,
                }
                for task in self.pending_tasks
            ],
        }
