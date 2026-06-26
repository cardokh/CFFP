"""CCore pipeline API routes."""
from __future__ import annotations

from urllib.parse import unquote

from backend.src.ccore.pipelines.pipeline_contracts import CCorePipelineRequestParser
from backend.src.ccore.pipelines.pipeline_mapper import CCorePipelineMapper
from backend.src.ccore.pipelines.pipeline_messages import (
    CCORE_PIPELINE_CREATED_SUCCESS_MESSAGE,
    CCORE_PIPELINE_DELETED_SUCCESS_MESSAGE,
    CCORE_PIPELINE_INVALID_ID_MESSAGE,
    CCORE_PIPELINE_INVALID_JSON_BODY_MESSAGE,
    CCORE_PIPELINE_NOT_FOUND_MESSAGE,
    CCORE_PIPELINE_UPDATED_SUCCESS_MESSAGE,
)
from src.api.api_paths import API_PATH_CCORE_PIPELINES_PREFIX
from src.api.route_utils import read_json_body, send_json

ccore_pipeline_mapper = CCorePipelineMapper()
ccore_pipeline_request_parser = CCorePipelineRequestParser()


def handle_get_ccore_pipelines(handler, ccore_pipeline_service) -> None:
    try:
        pipelines = ccore_pipeline_service.get_all_pipelines()
    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return
    send_json(handler, 200, {"success": True, "pipelines": ccore_pipeline_mapper.domains_to_response(pipelines)})


def handle_get_ccore_pipeline_statuses(handler, ccore_pipeline_status_service) -> None:
    try:
        statuses = ccore_pipeline_status_service.get_all_statuses()
    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return
    send_json(handler, 200, {"success": True, "pipelineStatuses": ccore_pipeline_mapper.statuses_to_response(statuses)})


def handle_get_ccore_pipeline_by_id(handler, ccore_pipeline_service, path: str) -> None:
    try:
        pipeline_id = extract_ccore_pipeline_id(path)
        pipeline = ccore_pipeline_service.get_pipeline_by_id(pipeline_id)
    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return
    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return
    if pipeline is None:
        send_json(handler, 404, {"success": False, "error": CCORE_PIPELINE_NOT_FOUND_MESSAGE})
        return
    send_json(handler, 200, {"success": True, "pipeline": ccore_pipeline_mapper.domain_to_response(pipeline)})


def handle_create_ccore_pipeline(handler, ccore_pipeline_service) -> None:
    request_data = read_json_body(handler)
    if request_data is None:
        send_json(handler, 400, {"success": False, "error": CCORE_PIPELINE_INVALID_JSON_BODY_MESSAGE})
        return
    try:
        create_request = ccore_pipeline_request_parser.parse_create_request(request_data)
        pipeline = ccore_pipeline_mapper.create_request_to_domain(create_request)
        created_pipeline = ccore_pipeline_service.create_pipeline(pipeline)
    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return
    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return
    send_json(handler, 201, {"success": True, "message": CCORE_PIPELINE_CREATED_SUCCESS_MESSAGE, "pipeline": ccore_pipeline_mapper.domain_to_response(created_pipeline)})


def handle_update_ccore_pipeline(handler, ccore_pipeline_service, path: str) -> None:
    request_data = read_json_body(handler)
    if request_data is None:
        send_json(handler, 400, {"success": False, "error": CCORE_PIPELINE_INVALID_JSON_BODY_MESSAGE})
        return
    try:
        pipeline_id = extract_ccore_pipeline_id(path)
        update_request = ccore_pipeline_request_parser.parse_update_request(pipeline_id, request_data)
        pipeline = ccore_pipeline_mapper.update_request_to_domain(update_request)
        updated_pipeline = ccore_pipeline_service.update_pipeline(pipeline)
    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return
    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return
    if updated_pipeline is None:
        send_json(handler, 404, {"success": False, "error": CCORE_PIPELINE_NOT_FOUND_MESSAGE})
        return
    send_json(handler, 200, {"success": True, "message": CCORE_PIPELINE_UPDATED_SUCCESS_MESSAGE, "pipeline": ccore_pipeline_mapper.domain_to_response(updated_pipeline)})


def handle_delete_ccore_pipeline(handler, ccore_pipeline_service, path: str) -> None:
    try:
        pipeline_id = extract_ccore_pipeline_id(path)
        deleted = ccore_pipeline_service.delete_pipeline(pipeline_id)
    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return
    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return
    if not deleted:
        send_json(handler, 404, {"success": False, "error": CCORE_PIPELINE_NOT_FOUND_MESSAGE})
        return
    send_json(handler, 200, {"success": True, "message": CCORE_PIPELINE_DELETED_SUCCESS_MESSAGE})


def extract_ccore_pipeline_id(path: str) -> str:
    if not path.startswith(API_PATH_CCORE_PIPELINES_PREFIX):
        raise ValueError(CCORE_PIPELINE_INVALID_ID_MESSAGE)
    pipeline_id = unquote(path[len(API_PATH_CCORE_PIPELINES_PREFIX):]).strip("/")
    if not pipeline_id:
        raise ValueError(CCORE_PIPELINE_INVALID_ID_MESSAGE)
    return pipeline_id
