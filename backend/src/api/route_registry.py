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
    API_PATH_AUTOMATION_PIPELINES,
    API_PATH_AUTOMATION_PIPELINES_PREFIX,
    API_PATH_AUTOMATION_TASKS,
    API_PATH_AUTOMATION_TASKS_PREFIX,
    API_PATH_AUTH_FORGOT_PASSWORD,
    API_PATH_AUTH_LOGIN,
    API_PATH_AUTH_REGISTER,
    API_PATH_CCORE_METRICS,
    API_PATH_CCORE_METRICS_PREFIX,
    API_PATH_CCORE_METRIC_TYPES,
    API_PATH_CCORE_TASKS,
    API_PATH_CCORE_TASKS_PREFIX,
    API_PATH_CCORE_TASK_STATUSES,
    API_PATH_CCORE_EXECUTION_PROVIDERS,
    API_PATH_CCORE_EXECUTION_IMPLEMENTERS,
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
from src.core.automation.automation_pipeline_routes import (
    handle_get_automation_pipeline_by_id,
    handle_get_automation_pipelines,
)
from src.core.automation.automation_task_routes import (
    handle_execute_automation_task_path,
    handle_get_automation_task_path,
    handle_get_automation_tasks,
    handle_validate_automation_task_path,
)
from backend.src.ccore.metrics.metric_routes import (
    handle_create_ccore_metric,
    handle_delete_ccore_metric,
    handle_get_ccore_metric_by_id,
    handle_get_ccore_metric_types,
    handle_get_ccore_metrics,
    handle_update_ccore_metric,
)
from backend.src.ccore.tasks.task_routes import (
    handle_create_ccore_task,
    handle_delete_ccore_task,
    handle_get_ccore_task_path,
    handle_get_ccore_task_statuses,
    handle_get_ccore_execution_providers,
    handle_get_ccore_execution_implementers,
    handle_get_ccore_tasks,
    handle_post_ccore_task_path,
    handle_update_ccore_task,
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


def handle_execute_or_validate_automation_task_path(
    handler,
    automation_task_service,
    path,
) -> None:
    if path.endswith("/execute"):
        handle_execute_automation_task_path(
            handler,
            automation_task_service,
            path,
        )
        return

    handle_validate_automation_task_path(
        handler,
        automation_task_service,
        path,
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
                API_PATH_AUTOMATION_TASKS: lambda: handle_get_automation_tasks(
                    handler,
                    services.automation_task_service,
                ),
                API_PATH_AUTOMATION_PIPELINES: lambda: handle_get_automation_pipelines(
                    handler,
                    services.automation_pipeline_service,
                ),
                API_PATH_CCORE_TASKS: lambda: handle_get_ccore_tasks(
                    handler,
                    services.ccore_task_service,
                ),
                API_PATH_CCORE_TASK_STATUSES: lambda: handle_get_ccore_task_statuses(
                    handler,
                    services.ccore_task_status_service,
                ),
                API_PATH_CCORE_EXECUTION_PROVIDERS: lambda: handle_get_ccore_execution_providers(
                    handler,
                    services.task_execution_service,
                ),
                API_PATH_CCORE_EXECUTION_IMPLEMENTERS: lambda: handle_get_ccore_execution_implementers(
                    handler,
                    services.task_execution_service,
                ),
                API_PATH_CCORE_METRICS: lambda: handle_get_ccore_metrics(
                    handler,
                    services.ccore_metric_service,
                ),
                API_PATH_CCORE_METRIC_TYPES: lambda: handle_get_ccore_metric_types(
                    handler,
                    services.ccore_metric_type_service,
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
                API_PATH_AUTOMATION_TASKS_PREFIX: lambda path: handle_get_automation_task_path(
                    handler,
                    services.automation_task_service,
                    path,
                ),
                API_PATH_AUTOMATION_PIPELINES_PREFIX: lambda path: handle_get_automation_pipeline_by_id(
                    handler,
                    services.automation_pipeline_service,
                    path,
                ),
                API_PATH_CCORE_TASKS_PREFIX: lambda path: handle_get_ccore_task_path(
                    handler,
                    services.ccore_task_service,
                    path,
                ),
                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_get_ccore_metric_by_id(
                    handler,
                    services.ccore_metric_service,
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
                API_PATH_CCORE_TASKS: lambda: handle_create_ccore_task(
                    handler,
                    services.ccore_task_service,
                ),
                API_PATH_CCORE_METRICS: lambda: handle_create_ccore_metric(
                    handler,
                    services.ccore_metric_service,
                ),
            },
            "prefix": {
                API_PATH_AUTOMATION_TASKS_PREFIX: lambda path: handle_execute_or_validate_automation_task_path(
                    handler,
                    services.automation_task_service,
                    path,
                ),
                API_PATH_CCORE_TASKS_PREFIX: lambda path: handle_post_ccore_task_path(
                    handler,
                    services.task_execution_service,
                    path,
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
                API_PATH_CCORE_TASKS_PREFIX: lambda path: handle_update_ccore_task(
                    handler,
                    services.ccore_task_service,
                    path,
                ),
                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_update_ccore_metric(
                    handler,
                    services.ccore_metric_service,
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
                API_PATH_CCORE_TASKS_PREFIX: lambda path: handle_delete_ccore_task(
                    handler,
                    services.ccore_task_service,
                    path,
                ),
                API_PATH_CCORE_METRICS_PREFIX: lambda path: handle_delete_ccore_metric(
                    handler,
                    services.ccore_metric_service,
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
