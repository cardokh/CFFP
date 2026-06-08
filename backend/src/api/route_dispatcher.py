"""
Reusable API route dispatch helpers.

Responsibilities:
- Centralize exact-route and prefix-route dispatch logic.
- Keep app.py focused on HTTP method entry points instead of route-matching details.
- Reduce repeated route-matching boilerplate.
- Prepare for future route registration/table-based routing.
- Provide a method-aware request dispatcher for reusable API routing.
- Define clear dispatcher-compatible route registry types.

Architecture:
app.py -> route_dispatcher -> route handlers

Current scope:
- Supports exact routes where the handler receives no path argument.
- Supports prefix routes where the handler receives the matched request path.
- Supports method-aware route groups through dispatch_request().
- Returns True when a route is handled, False when no route matches.
- Exposes reusable route registry type aliases for route registries and utilities.
"""

from collections.abc import Callable

ExactRouteHandler = Callable[[], None]
PrefixRouteHandler = Callable[[str], None]

ExactRouteMap = dict[str, ExactRouteHandler]
PrefixRouteMap = dict[str, PrefixRouteHandler]

RouteGroup = dict[str, ExactRouteMap | PrefixRouteMap]
RouteRegistry = dict[str, RouteGroup]

ROUTE_GROUP_EXACT = "exact"
ROUTE_GROUP_PREFIX = "prefix"


def dispatch_exact_route(
    path: str,
    route_map: ExactRouteMap,
) -> bool:
    """
    Dispatch a request path to a handler using exact path matching.

    Args:
        path: Parsed request path without query string.
        route_map: Mapping from exact API path to handler function.

    Returns:
        True if a matching route was found and handled, otherwise False.
    """
    handler_function = route_map.get(path)

    if handler_function is None:
        return False

    handler_function()
    return True


def dispatch_prefix_route(
    path: str,
    route_map: PrefixRouteMap,
) -> bool:
    """
    Dispatch a request path to a handler using prefix path matching.

    Prefix routes are currently used for routes containing path identifiers, for example:
    /api/admin/users/3

    More specific/longer prefixes are matched first to avoid generic prefixes
    accidentally intercepting nested routes.

    Args:
        path: Parsed request path without query string.
        route_map: Mapping from API path prefix to handler function.

    Returns:
        True if a matching route prefix was found and handled, otherwise False.
    """
    sorted_route_items = sorted(
        route_map.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for route_prefix, handler_function in sorted_route_items:
        if path.startswith(route_prefix):
            handler_function(path)
            return True

    return False


def dispatch_route(
    path: str,
    exact_routes: ExactRouteMap | None = None,
    prefix_routes: PrefixRouteMap | None = None,
) -> bool:
    """
    Dispatch a request path using exact routes first, then prefix routes.

    Exact routes are checked before prefix routes to avoid accidental prefix matches
    taking priority over specific route definitions.

    Args:
        path: Parsed request path without query string.
        exact_routes: Optional mapping of exact paths to no-argument handlers.
        prefix_routes: Optional mapping of route prefixes to path-aware handlers.

    Returns:
        True if the request was handled, otherwise False.
    """
    if exact_routes and dispatch_exact_route(path, exact_routes):
        return True

    if prefix_routes and dispatch_prefix_route(path, prefix_routes):
        return True

    return False


def dispatch_request(
    method: str,
    path: str,
    routes_by_method: RouteRegistry,
) -> bool:
    """
    Dispatch a request using method-aware route groups.

    This function is the first step toward table-based routing. It allows app.py to
    define routes grouped by HTTP method instead of manually repeating route-matching
    control flow inside do_GET, do_POST, do_PUT, and do_DELETE.

    Expected route structure:

        {
            "GET": {
                "exact": {
                    "/api/health": handle_health,
                },
                "prefix": {
                    "/api/admin/users/": handle_get_user_by_id,
                },
            },
            "POST": {
                "exact": {
                    "/api/auth/login": handle_login,
                },
            },
        }

    Args:
        method: HTTP method name, for example "GET" or "POST".
        path: Parsed request path without query string.
        routes_by_method: Method-grouped route map.

    Returns:
        True if the request was handled, otherwise False.
    """
    route_group = routes_by_method.get(method)

    if route_group is None:
        return False

    exact_routes = route_group.get(ROUTE_GROUP_EXACT)
    prefix_routes = route_group.get(ROUTE_GROUP_PREFIX)

    return dispatch_route(
        path,
        exact_routes=exact_routes,
        prefix_routes=prefix_routes,
    )
