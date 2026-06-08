"""
Lesson category API routes.

Responsibilities:
- Handle lesson category CRUD route actions.
- Keep lesson category endpoint logic out of app.py.
- Convert HTTP/JSON request data into lesson category request contracts.
- Use mapper to convert request contracts into domain objects.
- Delegate domain-level CRUD use cases to LessonCategoryService.
- Convert returned domain objects into API-friendly response structures.
- Return consistent JSON API responses.

Architecture:
app.py -> route_registry -> lesson_category_routes -> request contract
-> LessonCategoryMapper -> LessonCategoryService -> LessonCategoryValidator
-> LessonCategoryRepository -> SQLite
"""

from src.api.route_utils import (
    extract_path_id,
    read_json_body,
    send_json,
)
from src.modules.lla.lesson_categories.lesson_category_contracts import (
    CreateLessonCategoryRequest,
    UpdateLessonCategoryRequest,
)
from src.modules.lla.lesson_categories.lesson_category_mapper import (
    LessonCategoryMapper,
)
from src.modules.lla.lesson_categories.lesson_category_messages import (
    INVALID_CATEGORY_ID_MESSAGE,
    INVALID_JSON_BODY_MESSAGE,
    LESSON_CATEGORY_CREATED_SUCCESS_MESSAGE,
    LESSON_CATEGORY_DELETED_SUCCESS_MESSAGE,
    LESSON_CATEGORY_NOT_FOUND_MESSAGE,
    LESSON_CATEGORY_UPDATED_SUCCESS_MESSAGE,
)

lesson_category_mapper = LessonCategoryMapper()


def handle_get_lesson_categories(handler, lesson_category_service) -> None:
    lesson_categories = lesson_category_service.get_all_lesson_categories()

    lesson_category_responses = [
        lesson_category_mapper.domain_to_details(lesson_category).to_camel_dict()
        for lesson_category in lesson_categories
    ]

    send_json(
        handler,
        200,
        {
            "success": True,
            "lessonCategories": lesson_category_responses,
        },
    )


def handle_get_lesson_category_by_id(
    handler,
    lesson_category_service,
    path: str,
) -> None:
    try:
        category_id = extract_path_id(path)
        lesson_category_lookup = lesson_category_mapper.category_id_to_domain(
            category_id
        )

        lesson_category = lesson_category_service.get_lesson_category_by_id(
            lesson_category_lookup
        )

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if lesson_category is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": LESSON_CATEGORY_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "lessonCategory": lesson_category_mapper.domain_to_details(
                lesson_category
            ).to_camel_dict(),
        },
    )


def handle_create_lesson_category(handler, lesson_category_service) -> None:
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_JSON_BODY_MESSAGE,
            },
        )
        return

    try:
        create_request = CreateLessonCategoryRequest(
            name=request_data.get("name", ""),
            description=request_data.get("description"),
            is_active=bool(
                request_data.get("isActive", request_data.get("is_active", True))
            ),
            updated_by=request_data.get("updated_by"),
        )

        lesson_category = lesson_category_mapper.create_request_to_domain(
            create_request
        )

        created_category = lesson_category_service.create_lesson_category(
            lesson_category
        )

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    send_json(
        handler,
        201,
        {
            "success": True,
            "message": LESSON_CATEGORY_CREATED_SUCCESS_MESSAGE,
            "lessonCategory": lesson_category_mapper.domain_to_details(
                created_category
            ).to_camel_dict(),
        },
    )


def handle_update_lesson_category(
    handler,
    lesson_category_service,
    path: str,
) -> None:
    try:
        category_id = extract_path_id(path)

    except ValueError:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_CATEGORY_ID_MESSAGE,
            },
        )
        return

    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_JSON_BODY_MESSAGE,
            },
        )
        return

    try:
        update_request = UpdateLessonCategoryRequest(
            category_id=category_id,
            name=request_data.get("name", ""),
            description=request_data.get("description"),
            is_active=bool(
                request_data.get("isActive", request_data.get("is_active", False))
            ),
            updated_by=request_data.get("updated_by"),
        )

        lesson_category = lesson_category_mapper.update_request_to_domain(
            update_request
        )

        updated_category = lesson_category_service.update_lesson_category(
            lesson_category
        )

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if updated_category is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": LESSON_CATEGORY_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": LESSON_CATEGORY_UPDATED_SUCCESS_MESSAGE,
            "lessonCategory": lesson_category_mapper.domain_to_details(
                updated_category
            ).to_camel_dict(),
        },
    )


def handle_delete_lesson_category(
    handler,
    lesson_category_service,
    path: str,
) -> None:
    try:
        category_id = extract_path_id(path)
        lesson_category = lesson_category_mapper.category_id_to_domain(category_id)

        was_deleted = lesson_category_service.delete_lesson_category(lesson_category)

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if not was_deleted:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": LESSON_CATEGORY_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": LESSON_CATEGORY_DELETED_SUCCESS_MESSAGE,
        },
    )
