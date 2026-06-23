from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Protocol


@dataclass
class TaskExecutionRequest:
    task_id: str
    execution_mode: str = "manual"
    requested_by: str = "system"
    input_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecutionContext:
    task_id: str
    task_name: str
    task_type: str
    provider_profile: str
    task_metadata: Dict[str, Any]
    input_payload: Dict[str, Any]
    execution_mode: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskExecutionResult:
    task_id: str
    status: str
    message: str
    provider_name: str
    execution_details: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[Dict[str, Any]] = None


class ExecutionProvider(Protocol):
    """Clean interface contract for replaceable execution infrastructure."""

    def run(self, context: TaskExecutionContext) -> TaskExecutionResult: ...
