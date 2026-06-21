"""Prefect implementation of the Factory execution provider."""

from __future__ import annotations

from src.core.factory.interfaces.llm_provider import ILlmProvider
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
    payload_keys: list[str],
    prompt: str,
    system_instruction: str | None,
    context_file_count: int,
) -> dict[str, object]:
    """Execute one primitive Factory task payload inside Prefect."""

    logger = get_run_logger()
    logger.info("Executing Factory task: %s (%s)", name, task_id)
    logger.info("Task definition path: %s", task_definition_path)
    logger.info("Task priority: %s", priority)
    logger.info("Task payload keys: %s", payload_keys)
    logger.info("Context file count: %s", context_file_count)
    logger.info("Prompt characters: %s", len(prompt))
    logger.info("System instruction characters: %s", len(system_instruction or ""))
    return {
        "task_id": task_id,
        "success": True,
        "message": "Factory task prepared by Prefect provider.",
    }


@flow(name="CCore Factory Task Execution")
def execute_factory_task_flow(
    task_id: str,
    name: str,
    task_definition_path: str,
    priority: int,
    payload_keys: list[str],
    prompt: str,
    system_instruction: str | None,
    context_file_count: int,
) -> dict[str, object]:
    """Run one Factory task execution flow with primitive parameters only."""

    return execute_factory_task_step(
        task_id=task_id,
        name=name,
        task_definition_path=task_definition_path,
        priority=priority,
        payload_keys=payload_keys,
        prompt=prompt,
        system_instruction=system_instruction,
        context_file_count=context_file_count,
    )


class PrefectExecutionProvider:
    """Executes Factory task requests through Prefect and an injected LLM provider."""

    def __init__(self, llm_provider: ILlmProvider) -> None:
        self._llm_provider = llm_provider

    def execute(self, request: FactoryTaskExecutionRequest) -> FactoryTaskExecutionResult:
        """Execute one Factory task request through a Prefect flow."""

        flow_result = execute_factory_task_flow(
            task_id=request.task_id,
            name=request.name,
            task_definition_path=request.task_definition_path,
            priority=request.priority,
            payload_keys=sorted(request.payload.keys()),
            prompt=request.prompt,
            system_instruction=request.system_instruction,
            context_file_count=request.context_file_count,
        )
        if not bool(flow_result["success"]):
            return FactoryTaskExecutionResult(
                task_id=str(flow_result["task_id"]),
                success=False,
                message=str(flow_result["message"]),
            )

        artifact_text = self._llm_provider.generate_artifact(
            prompt=request.prompt,
            system_instruction=request.system_instruction,
        )
        return FactoryTaskExecutionResult(
            task_id=str(flow_result["task_id"]),
            success=True,
            message=(
                "Factory task executed by Prefect provider; "
                f"generated artifact characters: {len(artifact_text)}."
            ),
            artifact_text=artifact_text,
        )
