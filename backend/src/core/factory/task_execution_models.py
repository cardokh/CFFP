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
    prompt: str = ""
    system_instruction: str | None = None
    context_file_count: int = 0


@dataclass(frozen=True)
class FactoryTaskExecutionResult:
    """Execution result returned by an execution provider."""

    task_id: str
    success: bool
    message: str
    artifact_text: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a serializable execution result."""

        return {
            "task_id": self.task_id,
            "success": self.success,
            "message": self.message,
            "artifact_text": self.artifact_text,
        }
