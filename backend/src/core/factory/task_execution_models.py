"""Factory task execution request and result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FactoryTaskExecutionRequest:
    """Primitive-only execution request passed to execution providers."""

    task_id: str
    name: str
    task_definition_path: str
    priority: int
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FactoryTaskExecutionResult:
    """Execution result returned by an execution provider."""

    task_id: str
    success: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        """Return a serializable execution result."""

        return {
            "task_id": self.task_id,
            "success": self.success,
            "message": self.message,
        }
