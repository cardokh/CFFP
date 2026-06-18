"""
Automation pipeline API routes.

Responsibilities:
- Handle automation pipeline HTTP requests.
- Delegate pipeline discovery to AutomationPipelineService.
- Return registered automation pipeline metadata for list/details views.
- Keep pipeline execution out of the first registry vertical slice.
"""

from json import JSONDecodeError
from urllib.parse import unquote

from src.api.api_paths import API_PATH_AUTOMATION_PIPELINES_PREFIX
from src.api.route_utils import send_json
from src.core.automation.automation_pipeline_mapper import (
    automation_pipeline_detail_to_response,
    automation_pipelines_to_response,
)
from src.core.automation.automation_pipeline_messages import (
    AUTOMATION_PIPELINE_NOT_FOUND,
    AUTOMATION_PIPELINE_REGISTRY_INVALID,
    AUTOMATION_PIPELINE_REGISTRY_LOAD_FAILED,
)


def handle_get_automation_pipelines(handler, automation_pipeline_service) -> None:
    try:
        automation_pipelines = automation_pipeline_service.get_all_pipelines()

    except FileNotFoundError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_PIPELINE_REGISTRY_LOAD_FAILED,
            },
        )
        return

    except JSONDecodeError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_PIPELINE_REGISTRY_INVALID,
            },
        )
        return

    response = automation_pipelines_to_response(automation_pipelines)

    send_json(
        handler,
        200,
        response,
    )


def handle_get_automation_pipeline_by_id(
    handler,
    automation_pipeline_service,
    path,
) -> None:
    pipeline_id = extract_automation_pipeline_id_from_path(path)

    try:
        automation_pipeline = automation_pipeline_service.get_pipeline_by_id(
            pipeline_id=pipeline_id,
        )

    except FileNotFoundError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_PIPELINE_REGISTRY_LOAD_FAILED,
            },
        )
        return

    except JSONDecodeError:
        send_json(
            handler,
            500,
            {
                "success": False,
                "error": AUTOMATION_PIPELINE_REGISTRY_INVALID,
            },
        )
        return

    if automation_pipeline is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": AUTOMATION_PIPELINE_NOT_FOUND,
            },
        )
        return

    response = automation_pipeline_detail_to_response(
        automation_pipeline,
    )

    send_json(
        handler,
        200,
        response,
    )


def extract_automation_pipeline_id_from_path(path: str) -> str:
    return unquote(
        path.replace(
            API_PATH_AUTOMATION_PIPELINES_PREFIX,
            "",
            1,
        ).strip()
    )
