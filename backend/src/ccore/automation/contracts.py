from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Protocol


@dataclass
class TaskExecutionRequest:
    task_id: str
    execution_provider_id: int
    execution_implementer_type_id: int
    execution_target_id: int
    execution_configuration_id: int
    requested_by: str = "system"
    input_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecutionContext:
    task_id: str
    task_name: str
    task_type: str
    execution_provider_id: int
    provider_label: str
    execution_implementer_type_id: int
    implementer_type_label: str
    execution_target_id: int
    target_label: str
    target_reference: str
    execution_configuration_id: int
    configuration_label: str
    configuration_description: Optional[str]
    configuration_elements: Dict[str, str]
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
    implementer_type_name: str
    target_name: str
    configuration_name: str
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
