"""
Shared API route utilities.

Responsibilities:
- Provide reusable HTTP response helpers.
- Provide reusable JSON request-body parsing.
- Provide reusable path identifier extraction.
- Keep route modules and app.py smaller and more consistent.

Architecture:
API Route Handler -> route_utils -> BaseHTTPRequestHandler response/request APIs

These helpers are intentionally small and framework-independent because the
project currently uses Python's built-in http.server module rather than Flask,
FastAPI, or Django.
"""

import json

from src.api.api_constants import (
    ALLOWED_CORS_ORIGINS,
    CONTENT_TYPE_JSON_UTF8,
    DEFAULT_CONTENT_LENGTH,
    HTTP_ALLOWED_METHODS,
    HTTP_HEADER_ACCESS_CONTROL_ALLOW_HEADERS,
    HTTP_HEADER_ACCESS_CONTROL_ALLOW_METHODS,
    HTTP_HEADER_ACCESS_CONTROL_ALLOW_ORIGIN,
    HTTP_HEADER_CONTENT_LENGTH,
    HTTP_HEADER_CONTENT_TYPE,
    HTTP_HEADER_ORIGIN,
    PATH_SEPARATOR,
    TEXT_ENCODING_UTF8,
)


def set_cors_headers(handler) -> None:
    origin = handler.headers.get(HTTP_HEADER_ORIGIN)

    if origin in ALLOWED_CORS_ORIGINS:
        handler.send_header(
            HTTP_HEADER_ACCESS_CONTROL_ALLOW_ORIGIN,
            origin,
        )

    handler.send_header(
        HTTP_HEADER_ACCESS_CONTROL_ALLOW_METHODS,
        HTTP_ALLOWED_METHODS,
    )

    handler.send_header(
        HTTP_HEADER_ACCESS_CONTROL_ALLOW_HEADERS,
        HTTP_HEADER_CONTENT_TYPE,
    )


def send_json(handler, status_code: int, payload: dict) -> None:
    response_body = json.dumps(payload).encode(TEXT_ENCODING_UTF8)

    handler.send_response(status_code)

    handler.send_header(
        HTTP_HEADER_CONTENT_TYPE,
        CONTENT_TYPE_JSON_UTF8,
    )

    handler.send_header(
        HTTP_HEADER_CONTENT_LENGTH,
        str(len(response_body)),
    )

    set_cors_headers(handler)

    handler.end_headers()
    handler.wfile.write(response_body)


def read_json_body(handler):
    try:
        content_length = int(
            handler.headers.get(
                HTTP_HEADER_CONTENT_LENGTH,
                DEFAULT_CONTENT_LENGTH,
            )
        )

        raw_body = handler.rfile.read(content_length)

        return json.loads(raw_body.decode(TEXT_ENCODING_UTF8))

    except (ValueError, json.JSONDecodeError):
        return None


def split_path_segments(path: str) -> list[str]:
    return [
        segment
        for segment in path.strip(PATH_SEPARATOR).split(PATH_SEPARATOR)
        if segment
    ]


def extract_path_id(path: str) -> int:
    return int(split_path_segments(path)[-1])


def extract_path_id_at_index(path: str, index: int) -> int:
    return int(split_path_segments(path)[index])
