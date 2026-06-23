from prefect import flow, task

from .contracts import (
    ExecutionProvider,
    TaskExecutionContext,
    TaskExecutionResult,
)


@task(name="Execute CCore Core Payload")
def execute_core_payload(context_dict: dict) -> dict:
    metadata = context_dict.get("task_metadata", {})

    if metadata.get("ai_assisted", False):
        return {
            "execution_summary": "AI cognitive processing boundary completed successfully."
        }

    return {
        "execution_summary": (
            f"Executed baseline task code for {context_dict['task_name']}."
        )
    }


@flow(name="CCore Orchestration Flow")
def run_ccore_task_flow(context_dict: dict) -> dict:
    return execute_core_payload(context_dict)


class PrefectExecutionProvider(ExecutionProvider):
    def run(self, context: TaskExecutionContext) -> TaskExecutionResult:
        context_dict = {
            "task_id": context.task_id,
            "task_name": context.task_name,
            "task_type": context.task_type,
            "task_metadata": context.task_metadata,
            "input_payload": context.input_payload,
        }

        try:
            flow_state = run_ccore_task_flow(context_dict)
            return TaskExecutionResult(
                task_id=context.task_id,
                status="COMPLETED",
                message="Prefect flow execution completed successfully.",
                provider_name="PrefectExecutionProvider",
                execution_details={"summary": flow_state},
            )
        except Exception as exc:
            return TaskExecutionResult(
                task_id=context.task_id,
                status="FAILED",
                message=f"Prefect execution run failed: {str(exc)}",
                provider_name="PrefectExecutionProvider",
                error_details={
                    "exception": type(exc).__name__,
                    "message": str(exc),
                },
            )
