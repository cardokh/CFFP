"""
Route dispatcher tests.

Responsibilities:
- Verify reusable dispatcher behavior independently from HTTP transport.
- Protect route dispatch precedence and matching behavior during refactors.
- Provide regression safety for future route/plugin architecture work.

Architecture:
tests -> route_dispatcher
"""

from src.api.route_dispatcher import (
    dispatch_exact_route,
    dispatch_prefix_route,
    dispatch_request,
)
from src.api.http_methods import (
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
)


def test_dispatch_exact_route_calls_matching_handler() -> None:
    called = {"value": False}

    def handler() -> None:
        called["value"] = True

    handled = dispatch_exact_route(
        path="/api/health",
        route_map={
            "/api/health": handler,
        },
    )

    assert handled is True
    assert called["value"] is True


def test_dispatch_exact_route_returns_false_when_missing() -> None:
    handled = dispatch_exact_route(
        path="/api/missing",
        route_map={
            "/api/health": lambda: None,
        },
    )

    assert handled is False


def test_dispatch_prefix_route_calls_matching_handler() -> None:
    captured = {"path": None}

    def handler(path: str) -> None:
        captured["path"] = path

    handled = dispatch_prefix_route(
        path="/api/admin/users/5",
        route_map={
            "/api/admin/users/": handler,
        },
    )

    assert handled is True
    assert captured["path"] == "/api/admin/users/5"


def test_dispatch_prefix_route_returns_false_when_missing() -> None:
    handled = dispatch_prefix_route(
        path="/api/unknown",
        route_map={
            "/api/admin/users/": lambda path: None,
        },
    )

    assert handled is False


def test_dispatch_request_uses_http_method_group() -> None:
    called = {"value": False}

    def get_handler() -> None:
        called["value"] = True

    handled = dispatch_request(
        method=HTTP_METHOD_GET,
        path="/api/health",
        routes_by_method={
            HTTP_METHOD_GET: {
                "exact": {
                    "/api/health": get_handler,
                },
            },
        },
    )

    assert handled is True
    assert called["value"] is True


def test_dispatch_request_returns_false_for_unknown_method() -> None:
    handled = dispatch_request(
        method=HTTP_METHOD_POST,
        path="/api/health",
        routes_by_method={
            HTTP_METHOD_GET: {
                "exact": {
                    "/api/health": lambda: None,
                },
            },
        },
    )

    assert handled is False


def test_exact_routes_take_priority_over_prefix_routes() -> None:
    execution_order = []

    def exact_handler() -> None:
        execution_order.append("exact")

    def prefix_handler(path: str) -> None:
        execution_order.append("prefix")

    handled = dispatch_request(
        method=HTTP_METHOD_GET,
        path="/api/admin/users",
        routes_by_method={
            HTTP_METHOD_GET: {
                "exact": {
                    "/api/admin/users": exact_handler,
                },
                "prefix": {
                    "/api/admin/": prefix_handler,
                },
            },
        },
    )

    assert handled is True
    assert execution_order == ["exact"]
