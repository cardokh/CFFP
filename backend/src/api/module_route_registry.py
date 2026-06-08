"""
Module route registry composition.

Responsibilities:
- Define how feature/application modules contribute API routes.
- Keep module route builders registered in one lightweight composition point.
- Prepare for a future plugin/module registration model without introducing plugin loading yet.
- Keep route_registry.py focused on final application route composition.

Architecture:
route_registry -> module_route_registry -> module-owned route registries
"""

from collections.abc import Callable

from src.api.modules.lla.routes.lla_route_registry import build_lla_route_registry
from src.api.route_dispatcher import RouteRegistry

ModuleRouteRegistryBuilder = Callable[[object, object], RouteRegistry]

MODULE_ROUTE_REGISTRY_BUILDERS: tuple[ModuleRouteRegistryBuilder, ...] = (
    build_lla_route_registry,
)


def build_module_route_registries(
    handler,
    services,
) -> list[RouteRegistry]:
    return [
        build_module_route_registry(
            handler,
            services,
        )
        for build_module_route_registry in MODULE_ROUTE_REGISTRY_BUILDERS
    ]
