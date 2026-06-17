"""
Route registry composition tests.

Responsibilities:
- Verify application route registry composition behavior.
- Protect core/platform and LLA route registration during refactors.
- Ensure reusable route-registry merge behavior remains stable.

Architecture:
tests -> route_registry -> module registries -> dispatcher contracts
"""

from types import SimpleNamespace

from src.api.api_paths import (
    API_PATH_ADMIN_USERS,
    API_PATH_AUTOMATION_TASKS,
    API_PATH_HEALTH,
)
from src.api.http_methods import (
    HTTP_METHOD_DELETE,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
)
from src.api.modules.lla.lla_api_paths import (
    API_PATH_ADMIN_LEARNING_ITEMS,
    API_PATH_ADMIN_LESSON_CATEGORIES,
    API_PATH_ADMIN_LESSON_FORM_OPTIONS,
    API_PATH_ADMIN_LESSONS,
    API_PATH_ADMIN_QUIZ_QUESTIONS,
)
from src.api.route_dispatcher import (
    ROUTE_GROUP_EXACT,
    ROUTE_GROUP_PREFIX,
)
from src.api.route_registry import (
    build_api_route_registry,
    build_core_route_registry,
)
from src.api.route_registry_utils import merge_route_registries


class DummyHandler:
    def _send_json(self, status_code: int, payload: dict) -> None:
        pass


def build_dummy_services() -> SimpleNamespace:
    dummy_service = object()

    return SimpleNamespace(
        users_service=dummy_service,
        auth_service=dummy_service,
        register_service=dummy_service,
        lesson_category_service=dummy_service,
        learning_item_service=dummy_service,
        quiz_question_service=dummy_service,
        lesson_service=dummy_service,
        reference_data_service=dummy_service,
        ai_speech_service=dummy_service,
        ai_speech_validator=dummy_service,
        automation_task_service=dummy_service,
    )


def test_build_core_route_registry_contains_health_route() -> None:
    route_registry = build_core_route_registry(
        handler=DummyHandler(),
        services=build_dummy_services(),
    )

    assert API_PATH_HEALTH in route_registry[HTTP_METHOD_GET][ROUTE_GROUP_EXACT]


def test_build_core_route_registry_contains_automation_tasks_route() -> None:
    route_registry = build_core_route_registry(
        handler=DummyHandler(),
        services=build_dummy_services(),
    )

    assert API_PATH_AUTOMATION_TASKS in route_registry[HTTP_METHOD_GET][ROUTE_GROUP_EXACT]


def test_build_core_route_registry_contains_users_route() -> None:
    route_registry = build_core_route_registry(
        handler=DummyHandler(),
        services=build_dummy_services(),
    )

    assert API_PATH_ADMIN_USERS in route_registry[HTTP_METHOD_GET][ROUTE_GROUP_EXACT]


def test_build_api_route_registry_contains_lla_routes() -> None:
    route_registry = build_api_route_registry(
        handler=DummyHandler(),
        services=build_dummy_services(),
    )

    get_exact_routes = route_registry[HTTP_METHOD_GET][ROUTE_GROUP_EXACT]

    assert API_PATH_ADMIN_LESSON_CATEGORIES in get_exact_routes
    assert API_PATH_ADMIN_LEARNING_ITEMS in get_exact_routes
    assert API_PATH_ADMIN_QUIZ_QUESTIONS in get_exact_routes
    assert API_PATH_ADMIN_LESSONS in get_exact_routes
    assert API_PATH_ADMIN_LESSON_FORM_OPTIONS in get_exact_routes


def test_build_api_route_registry_contains_all_http_methods() -> None:
    route_registry = build_api_route_registry(
        handler=DummyHandler(),
        services=build_dummy_services(),
    )

    assert HTTP_METHOD_GET in route_registry
    assert HTTP_METHOD_POST in route_registry
    assert HTTP_METHOD_PUT in route_registry
    assert HTTP_METHOD_DELETE in route_registry


def test_merge_route_registries_combines_multiple_registries() -> None:
    registry_one = {
        HTTP_METHOD_GET: {
            ROUTE_GROUP_EXACT: {
                "/route-one": lambda: None,
            },
        },
    }

    registry_two = {
        HTTP_METHOD_GET: {
            ROUTE_GROUP_EXACT: {
                "/route-two": lambda: None,
            },
        },
    }

    merged_registry = merge_route_registries(
        registry_one,
        registry_two,
    )

    exact_routes = merged_registry[HTTP_METHOD_GET][ROUTE_GROUP_EXACT]

    assert "/route-one" in exact_routes
    assert "/route-two" in exact_routes
