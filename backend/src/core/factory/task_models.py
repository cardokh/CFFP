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
class FactoryTaskRunRecord:
    """Execution summary for one Factory task."""

    task_id: str
    name: str
    status: str
    message: str
    artifact_path: str | None = None
    report_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a serializable task run record."""

        data: dict[str, object] = {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }
        if self.artifact_path:
            data["artifact_path"] = self.artifact_path
        if self.report_path:
            data["report_path"] = self.report_path
        return data


@dataclass(frozen=True)
class FactoryRunnerResult:
    """Summary returned by the Factory task runner."""

    discovered_count: int
    executed_count: int
    completed_count: int
    failed_count: int
    task_runs: tuple[FactoryTaskRunRecord, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a serializable runner result."""

        return {
            "discovered_count": self.discovered_count,
            "executed_count": self.executed_count,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "task_runs": [record.to_dict() for record in self.task_runs],
        }
