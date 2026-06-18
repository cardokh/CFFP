"""
Automation task execution mapper.

Responsibilities:
- Convert automation task execution domain results into API responses.
- Keep execution transport field names out of services and routes.
- Provide a stable response contract for future pipeline orchestration.
"""

from src.core.automation.automation_task_mapper import automation_task_to_response


def automation_task_execution_result_to_response(task_execution_result) -> dict:
    return {
        "execution": {
            "execution_id": task_execution_result.execution_id,
            "task_id": task_execution_result.task_id,
            "status": task_execution_result.status,
            "stage": task_execution_result.stage,
            "message": task_execution_result.message,
            "started_at": task_execution_result.started_at,
            "finished_at": task_execution_result.finished_at,
            "duration_ms": task_execution_result.duration_ms,
            "return_code": task_execution_result.return_code,
            "stdout": task_execution_result.stdout,
            "stderr": task_execution_result.stderr,
            "validation": task_execution_result.validation,
            "execution_report": task_execution_result.execution_report,
        }
    }


def automation_task_execution_to_response(task_execution_result) -> dict:
    automation_task = task_execution_result["task"]

    response = {
        "task": automation_task_to_response(
            automation_task,
        ),
    }

    response.update(
        automation_task_execution_result_to_response(
            task_execution_result["execution"],
        )
    )

    return response


def automation_task_execution_history_to_response(task_execution_history_result) -> dict:
    return {
        "task": automation_task_to_response(
            task_execution_history_result["task"],
        ),
        "executions": task_execution_history_result["executions"],
    }


def automation_task_execution_report_to_response(task_execution_report_result) -> dict:
    return {
        "task": automation_task_to_response(
            task_execution_report_result["task"],
        ),
        "execution_report": task_execution_report_result["execution_report"],
    }
