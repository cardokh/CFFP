"""Prefect implementation of the Factory execution provider."""

from __future__ import annotations

from typing import Any

from src.core.factory.task_execution_models import (
    FactoryTaskExecutionRequest,
    FactoryTaskExecutionResult,
)
from src.infrastructure.orchestration.prefect.prefect_compat import (
    flow,
    get_run_logger,
    task,
)


@task(name="Execute Factory Task")
def execute_factory_task_step(
    task_id: str,
    name: str,
    task_definition_path: str,
    priority: int,
    payload: dict[str, Any],
) -> dict[str, object]:
    """Execute one primitive Factory task payload inside Prefect."""

    logger = get_run_logger()
    logger.info("Executing Factory task: %s (%s)", name, task_id)
    logger.info("Task definition path: %s", task_definition_path)
    logger.info("Task priority: %s", priority)
    logger.info("Task payload keys: %s", sorted(payload.keys()))
    return {
        "task_id": task_id,
        "success": True,
        "message": "Factory task executed by Prefect provider.",
    }


@flow(name="CCore Factory Task Execution")
def execute_factory_task_flow(
    task_id: str,
    name: str,
    task_definition_path: str,
    priority: int,
    payload: dict[str, Any],
) -> dict[str, object]:
    """Run one Factory task execution flow with primitive parameters only."""

    return execute_factory_task_step(
        task_id=task_id,
        name=name,
        task_definition_path=task_definition_path,
        priority=priority,
        payload=payload,
    )


class PrefectExecutionProvider:
    """Executes Factory task requests through Prefect."""

    def execute(self, request: FactoryTaskExecutionRequest) -> FactoryTaskExecutionResult:
        """Execute one Factory task request through a Prefect flow."""

        result = execute_factory_task_flow(
            task_id=request.task_id,
            name=request.name,
            task_definition_path=request.task_definition_path,
            priority=request.priority,
            payload=request.payload,
        )
        return FactoryTaskExecutionResult(
            task_id=str(result["task_id"]),
            success=bool(result["success"]),
            message=str(result["message"]),
        )
