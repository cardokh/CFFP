"""
API route registry builder.

Responsibilities:
- Build the application route registry used by the reusable route dispatcher.
- Keep route registration outside app.py.
- Keep domain route-handler wiring outside the core server entry point.
- Compose platform/core routes with module-owned route registries.
- Prepare for future plugin/module route registration.

Architecture:
app.py -> route_registry -> module_route_registry -> module route registries -> route_dispatcher -> route handlers

Current refactor stage:
- app.py no longer needs one wrapper method per route handler.
- LLA route registration lives in src.api.modules.lla.routes.lla_route_registry.
- Module route registry builders are collected in src.api.module_route_registry.
- Core/platform routes such as health, echo, authentication, users, and AI speech compose here.
- Route registry composition uses a reusable merge utility.
- HTTP method names are centralized in src.api.http_methods.
- Dispatcher-compatible route registry typing is centralized in route_dispatcher.py.
"""

from src.api.api_paths import (
    API_PATH_ADMIN_USERS,
    API_PATH_ADMIN_USERS_PREFIX,
    API_PATH_AI_SPEECH_GENERATE,
    API_PATH_AUTH_FORGOT_PASSWORD,
    API_PATH_AUTH_LOGIN,
    API_PATH_AUTH_REGISTER,
    API_PATH_ECHO_PREFIX,
    API_PATH_HEALTH,
)
from src.api.api_response_messages import (
    API_RESPONSE_MESSAGE_ECHO_WORKS,
    API_RESPONSE_STATUS_OK,
)
from src.api.http_methods import (
    HTTP_METHOD_DELETE,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
)
from src.api.module_route_registry import (
    build_module_route_registries,
)
from src.api.route_dispatcher import RouteRegistry
from src.api.route_registry_utils import (
    merge_route_registries,
)
from src.core.ai.ai_speech.ai_speech_routes import (
    handle_generate_ai_speech,
)
from src.core.users.user_routes import (
    handle_delete_user,
    handle_forgot_password,
    handle_get_user_by_id,
    handle_get_users,
    handle_login,
    handle_register,
    handle_update_user,
)


def build_core_route_registry(
    handler,
    services,
) -> RouteRegistry:
    return {
        HTTP_METHOD_GET: {
            "exact": {
                API_PATH_HEALTH: lambda: handler._send_json(
                    200,
                    {
                        "status": API_RESPONSE_STATUS_OK,
                    },
                ),
                API_PATH_ADMIN_USERS: lambda: handle_get_users(
                    handler,
                    services.users_service,
                ),
            },
            "prefix": {
                API_PATH_ECHO_PREFIX: lambda path: handler._send_json(
                    200,
                    {
                        "message": API_RESPONSE_MESSAGE_ECHO_WORKS,
                    },
                ),
                API_PATH_ADMIN_USERS_PREFIX: lambda path: handle_get_user_by_id(
                    handler,
                    services.users_service,
                    path,
                ),
            },
        },
        HTTP_METHOD_POST: {
            "exact": {
                API_PATH_AUTH_LOGIN: lambda: handle_login(
                    handler,
                    services.users_service,
                ),
                API_PATH_AUTH_REGISTER: lambda: handle_register(
                    handler,
                    services.users_service,
                ),
                API_PATH_AUTH_FORGOT_PASSWORD: lambda: handle_forgot_password(
                    handler,
                    services.users_service,
                ),
                API_PATH_AI_SPEECH_GENERATE: lambda: handle_generate_ai_speech(
                    handler,
                    services.ai_speech_service,
                    services.ai_speech_validator,
                ),
            },
        },
        HTTP_METHOD_PUT: {
            "prefix": {
                API_PATH_ADMIN_USERS_PREFIX: lambda path: handle_update_user(
                    handler,
                    services.users_service,
                    path,
                ),
            },
        },
        HTTP_METHOD_DELETE: {
            "prefix": {
                API_PATH_ADMIN_USERS_PREFIX: lambda path: handle_delete_user(
                    handler,
                    services.users_service,
                    path,
                ),
            },
        },
    }


def build_api_route_registry(
    handler,
    services,
) -> RouteRegistry:
    return merge_route_registries(
        build_core_route_registry(
            handler=handler,
            services=services,
        ),
        *build_module_route_registries(
            handler=handler,
            services=services,
        ),
    )
