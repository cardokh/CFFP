"""
CCore metric API routes.

Responsibilities:
- Handle CCore metric CRUD HTTP requests.
- Handle CCore metric reference-data requests.
- Delegate request payload parsing to API request contracts.
- Delegate business use cases to CCoreMetricService.
- Return consistent JSON responses.
"""

from urllib.parse import unquote

from src.api.api_paths import API_PATH_CCORE_METRICS_PREFIX
from src.api.route_utils import read_json_body, send_json
from backend.src.ccore.metrics.metric_contracts import CCoreMetricRequestParser
from backend.src.ccore.metrics.metric_mapper import CCoreMetricMapper
from backend.src.ccore.metrics.metric_messages import (
    CCORE_METRIC_CREATED_SUCCESS_MESSAGE,
    CCORE_METRIC_DELETED_SUCCESS_MESSAGE,
    CCORE_METRIC_INVALID_ID_MESSAGE,
    CCORE_METRIC_INVALID_JSON_BODY_MESSAGE,
    CCORE_METRIC_NOT_FOUND_MESSAGE,
    CCORE_METRIC_UPDATED_SUCCESS_MESSAGE,
)

ccore_metric_mapper = CCoreMetricMapper()
ccore_metric_request_parser = CCoreMetricRequestParser()


def handle_get_ccore_metrics(handler, ccore_metric_service) -> None:
    try:
        metrics = ccore_metric_service.get_all_metrics()

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "metrics": ccore_metric_mapper.domains_to_response(metrics),
        },
    )


def handle_get_ccore_metric_types(handler, ccore_metric_type_service) -> None:
    try:
        metric_types = ccore_metric_type_service.get_all_types()

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "metricTypes": ccore_metric_mapper.types_to_response(metric_types),
        },
    )


def handle_get_ccore_metric_by_id(handler, ccore_metric_service, path: str) -> None:
    metric_id = extract_ccore_metric_id(path)

    try:
        metric = ccore_metric_service.get_metric_by_id(metric_id)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    if metric is None:
        send_json(
            handler, 404, {"success": False, "error": CCORE_METRIC_NOT_FOUND_MESSAGE}
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "metric": ccore_metric_mapper.domain_to_response(metric),
        },
    )


def handle_create_ccore_metric(handler, ccore_metric_service) -> None:
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {"success": False, "error": CCORE_METRIC_INVALID_JSON_BODY_MESSAGE},
        )
        return

    try:
        create_request = ccore_metric_request_parser.parse_create_request(request_data)
        metric = ccore_metric_mapper.create_request_to_domain(create_request)
        created_metric = ccore_metric_service.create_metric(metric)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    send_json(
        handler,
        201,
        {
            "success": True,
            "message": CCORE_METRIC_CREATED_SUCCESS_MESSAGE,
            "metric": ccore_metric_mapper.domain_to_response(created_metric),
        },
    )


def handle_update_ccore_metric(handler, ccore_metric_service, path: str) -> None:
    metric_id = extract_ccore_metric_id(path)
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {"success": False, "error": CCORE_METRIC_INVALID_JSON_BODY_MESSAGE},
        )
        return

    try:
        update_request = ccore_metric_request_parser.parse_update_request(
            metric_id,
            request_data,
        )
        metric = ccore_metric_mapper.update_request_to_domain(update_request)
        updated_metric = ccore_metric_service.update_metric(metric)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    if updated_metric is None:
        send_json(
            handler, 404, {"success": False, "error": CCORE_METRIC_NOT_FOUND_MESSAGE}
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": CCORE_METRIC_UPDATED_SUCCESS_MESSAGE,
            "metric": ccore_metric_mapper.domain_to_response(updated_metric),
        },
    )


def handle_delete_ccore_metric(handler, ccore_metric_service, path: str) -> None:
    metric_id = extract_ccore_metric_id(path)

    try:
        deleted = ccore_metric_service.delete_metric(metric_id)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    except Exception as error:
        send_json(handler, 500, {"success": False, "error": str(error)})
        return

    if not deleted:
        send_json(
            handler, 404, {"success": False, "error": CCORE_METRIC_NOT_FOUND_MESSAGE}
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": CCORE_METRIC_DELETED_SUCCESS_MESSAGE,
        },
    )


def extract_ccore_metric_id(path: str) -> str:
    if not path.startswith(API_PATH_CCORE_METRICS_PREFIX):
        raise ValueError(CCORE_METRIC_INVALID_ID_MESSAGE)

    metric_id = unquote(path[len(API_PATH_CCORE_METRICS_PREFIX) :]).strip("/")

    if not metric_id:
        raise ValueError(CCORE_METRIC_INVALID_ID_MESSAGE)

    return metric_id
