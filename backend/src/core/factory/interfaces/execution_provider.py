"""Factory execution provider interface."""

from __future__ import annotations

from typing import Protocol

from src.core.factory.task_execution_models import (
    FactoryTaskExecutionRequest,
    FactoryTaskExecutionResult,
)


class IExecutionProvider(Protocol):
    """Contract for executing Factory work through an orchestration provider."""

    def execute(self, request: FactoryTaskExecutionRequest) -> FactoryTaskExecutionResult:
        """Execute one Factory task request."""
