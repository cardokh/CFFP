from endpoint_http_client import send_endpoint_request
from endpoint_payload_builder import build_endpoint_path


def read_response(response):
    try:
        return (
            "json",
            response.json(),
        )

    except ValueError:
        return (
            "text",
            response.text,
        )


def get_nested_value(
    source: dict,
    path: str,
):
    current_value = source

    for path_part in path.split("."):
        if not isinstance(current_value, dict) or path_part not in current_value:
            return None

        current_value = current_value[path_part]

    return current_value


def build_empty_endpoint_result(
    endpoint: dict,
    runtime_values: dict,
) -> dict:
    expected_success = endpoint.get(
        "expectedSuccess",
    )

    return {
        "suite": endpoint.get(
            "suite",
        ),
        "name": endpoint["name"],
        "method": endpoint["method"],
        "path": build_endpoint_path(
            endpoint,
            runtime_values,
        ),
        "configuredPath": endpoint["path"],
        "infrastructure": {
            "expectedStatusCode": endpoint["expectedStatusCode"],
            "actualStatusCode": None,
            "endpointAvailable": False,
            "success": False,
            "error": None,
        },
        "operation": {
            "expectedSuccess": expected_success,
            "actualSuccess": None,
            "success": None,
            "reason": None,
            "message": None,
        },
        "captures": {},
        "responseType": None,
        "responseBody": None,
    }


def evaluate_operation_success(
    endpoint: dict,
    response_body,
):
    expected_success = endpoint.get(
        "expectedSuccess",
    )

    if not isinstance(response_body, dict):
        return (
            None,
            None,
        )

    actual_success = response_body.get(
        "success",
    )

    if expected_success is None:
        return (
            actual_success,
            actual_success is not False,
        )

    return (
        actual_success,
        actual_success == expected_success,
    )


def apply_response_to_result(
    result: dict,
    response,
    endpoint: dict,
):
    response_type, response_body = read_response(
        response,
    )

    result["responseType"] = response_type

    result["responseBody"] = response_body

    infrastructure = result["infrastructure"]

    infrastructure["actualStatusCode"] = response.status_code

    infrastructure["endpointAvailable"] = True

    infrastructure["success"] = response.status_code == endpoint["expectedStatusCode"]

    if isinstance(response_body, dict):
        operation = result["operation"]

        actual_success, operation_passed = evaluate_operation_success(
            endpoint,
            response_body,
        )

        operation["actualSuccess"] = actual_success

        operation["success"] = operation_passed

        operation["reason"] = response_body.get(
            "reason",
        )

        operation["message"] = response_body.get(
            "message",
        )


def apply_captures(
    result: dict,
    endpoint: dict,
    runtime_values: dict,
) -> None:
    response_body = result.get(
        "responseBody",
    )

    if not isinstance(response_body, dict):
        return

    for runtime_key, response_path in endpoint.get(
        "capture",
        {},
    ).items():
        captured_value = get_nested_value(
            response_body,
            response_path,
        )

        result["captures"][runtime_key] = captured_value

        if captured_value is not None:
            runtime_values[runtime_key] = str(captured_value)


def run_endpoint_test(
    base_url: str,
    endpoint: dict,
    runtime_values: dict,
) -> dict:
    result = build_empty_endpoint_result(
        endpoint,
        runtime_values,
    )

    try:
        response = send_endpoint_request(
            base_url,
            endpoint,
            runtime_values,
        )

        apply_response_to_result(
            result,
            response,
            endpoint,
        )

        apply_captures(
            result,
            endpoint,
            runtime_values,
        )

    except Exception as error:
        result["infrastructure"]["error"] = str(error)

    return result
