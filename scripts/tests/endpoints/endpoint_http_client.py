import requests

from endpoint_constants import (
    HTTP_METHOD_DELETE,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
    REQUEST_TIMEOUT_SECONDS,
)
from endpoint_payload_builder import (
    build_endpoint_path,
    build_endpoint_payload,
)

REQUEST_METHODS = {
    HTTP_METHOD_GET: requests.get,
    HTTP_METHOD_POST: requests.post,
    HTTP_METHOD_PUT: requests.put,
    HTTP_METHOD_DELETE: requests.delete,
}


def build_endpoint_url(
    base_url: str,
    endpoint: dict,
    runtime_values: dict,
) -> str:
    return f"{base_url}{build_endpoint_path(endpoint, runtime_values)}"


def send_endpoint_request(
    base_url: str,
    endpoint: dict,
    runtime_values: dict,
):
    url = build_endpoint_url(
        base_url,
        endpoint,
        runtime_values,
    )

    method = endpoint["method"].upper()

    if method not in REQUEST_METHODS:
        raise ValueError(f"Unsupported HTTP method: {method}")

    request_function = REQUEST_METHODS[method]

    if method in [
        HTTP_METHOD_POST,
        HTTP_METHOD_PUT,
    ]:
        return request_function(
            url,
            json=build_endpoint_payload(
                endpoint,
                runtime_values,
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    return request_function(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
