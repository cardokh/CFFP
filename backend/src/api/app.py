"""
LLA Backend API Server

Responsibilities:
- Start the local HTTP API server.
- Dispatch incoming HTTP requests through reusable routing infrastructure.
- Coordinate API access to application services through the service container.
- Keep frontend/backend communication available during development.

Architecture:
Frontend -> API -> Route Dispatcher -> Route Handlers -> Services -> Repository -> SQLite Database

Current refactor stage:
- Shared low-level HTTP utilities have been moved to src.api.route_utils.
- Route dispatch behavior is centralized in src.api.route_dispatcher.
- Route registration has moved to src.api.route_registry.
- Service construction has moved to src.core.application.service_container.
- app.py is now a thin HTTP lifecycle/server entry point.
- HTTP method names are centralized in src.api.http_methods.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from src.api.api_constants import (
    API_SERVER_BASE_URL,
    API_SERVER_HOST,
    API_SERVER_PORT,
)
from src.api.api_response_messages import (
    API_RESPONSE_ERROR_NOT_FOUND,
)
from src.api.http_methods import (
    HTTP_METHOD_DELETE,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
)
from src.api.route_dispatcher import dispatch_request
from src.api.route_registry import build_api_route_registry
from src.api.route_utils import (
    read_json_body,
    send_json,
    set_cors_headers,
)
from src.core.application.service_container import build_service_container


class ApiRequestHandler(BaseHTTPRequestHandler):
    services = build_service_container()

    def _set_cors_headers(self) -> None:
        set_cors_headers(self)

    def _send_json(self, status_code: int, payload: dict) -> None:
        send_json(self, status_code, payload)

    def _read_json_body(self):
        return read_json_body(self)

    def _dispatch_api_request(self, method: str) -> None:
        parsed_url = urlparse(self.path)

        if dispatch_request(
            method=method,
            path=parsed_url.path,
            routes_by_method=build_api_route_registry(
                handler=self,
                services=self.services,
            ),
        ):
            return

        self._send_json(
            404,
            {"error": API_RESPONSE_ERROR_NOT_FOUND},
        )

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        self._dispatch_api_request(HTTP_METHOD_GET)

    def do_POST(self) -> None:
        self._dispatch_api_request(HTTP_METHOD_POST)

    def do_PUT(self) -> None:
        self._dispatch_api_request(HTTP_METHOD_PUT)

    def do_DELETE(self) -> None:
        self._dispatch_api_request(HTTP_METHOD_DELETE)


def run() -> None:
    server = ThreadingHTTPServer(
        (API_SERVER_HOST, API_SERVER_PORT),
        ApiRequestHandler,
    )

    print(f"API server running on {API_SERVER_BASE_URL}")

    server.serve_forever()


if __name__ == "__main__":
    run()
