from endpoint_http_client import send_endpoint_request


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


def build_empty_endpoint_result(endpoint: dict) -> dict:
    return {
        "name": endpoint["name"],
        "method": endpoint["method"],
        "path": endpoint["path"],
        "infrastructure": {
            "expectedStatusCode": endpoint["expectedStatusCode"],
            "actualStatusCode": None,
            "endpointAvailable": False,
            "success": False,
            "error": None,
        },
        "operation": {
            "success": None,
            "reason": None,
            "message": None,
        },
        "responseType": None,
        "responseBody": None,
    }


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

        operation["success"] = response_body.get(
            "success",
        )

        operation["reason"] = response_body.get(
            "reason",
        )

        operation["message"] = response_body.get(
            "message",
        )


def run_endpoint_test(
    base_url: str,
    endpoint: dict,
    runtime_values: dict,
) -> dict:
    result = build_empty_endpoint_result(
        endpoint,
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

    except Exception as error:
        result["infrastructure"]["error"] = str(error)

    return result
