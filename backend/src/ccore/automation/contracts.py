from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Protocol


@dataclass
class TaskExecutionRequest:
    task_id: str
    execution_provider_id: int
    execution_implementer_id: int
    requested_by: str = "system"
    input_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecutionContext:
    task_id: str
    task_name: str
    task_type: str
    execution_provider_id: int
    provider_label: str
    execution_implementer_id: int
    implementer_label: str
    task_metadata: Dict[str, Any]
    input_payload: Dict[str, Any]
    requested_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskExecutionResult:
    task_id: str
    status: str
    message: str
    provider_name: str
    implementer_name: str
    execution_details: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[Dict[str, Any]] = None


class ExecutionImplementer(Protocol):
    """Clean interface contract for replaceable execution implementers."""

    def execute(self, context: TaskExecutionContext) -> dict: ...


class ExecutionProvider(Protocol):
    """Clean interface contract for replaceable execution managers."""

    def run(
        self,
        context: TaskExecutionContext,
        implementer: ExecutionImplementer,
    ) -> TaskExecutionResult: ...
