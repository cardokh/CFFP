"""
Route registry utility functions.

Responsibilities:
- Provide reusable helpers for composing dispatcher-compatible route registries.
- Avoid duplicated nested route-registry merge logic.
- Keep central route composition readable as more modules are added.

Architecture:
route_registry -> route_registry_utils -> dispatcher-compatible route dictionaries
"""

from src.api.route_dispatcher import RouteRegistry


def merge_route_registries(
    *route_registries: RouteRegistry,
) -> RouteRegistry:
    merged_registry: RouteRegistry = {}

    for route_registry in route_registries:
        for method, route_groups in route_registry.items():
            merged_registry.setdefault(method, {})

            for match_type, routes in route_groups.items():
                merged_registry[method].setdefault(match_type, {})
                merged_registry[method][match_type].update(routes)

    return merged_registry
