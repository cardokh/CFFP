"""
Lesson API routes.

Responsibilities:
- Handle lesson CRUD route actions.
- Keep lesson endpoint logic out of app.py.
- Convert HTTP/JSON request data into lesson request contracts.
- Use mapper to convert request contracts into domain objects.
- Delegate domain-level CRUD use cases to LessonService.
- Convert returned domain objects into API-friendly response structures.
- Return consistent JSON API responses.

Architecture:
app.py -> route_registry -> lesson_routes -> request contract
-> LessonMapper -> LessonService -> LessonValidator -> LessonRepository -> SQLite
"""

from src.api.route_utils import (
    extract_path_id,
    read_json_body,
    send_json,
)
from src.modules.lla.lessons.lesson_contracts import (
    CreateLessonRequest,
    UpdateLessonRequest,
)
from src.modules.lla.lessons.lesson_mapper import LessonMapper
from src.modules.lla.lessons.lesson_messages import (
    INVALID_JSON_BODY_MESSAGE,
    INVALID_LESSON_ID_MESSAGE,
    LESSON_CREATED_SUCCESS_MESSAGE,
    LESSON_DELETED_SUCCESS_MESSAGE,
    LESSON_NOT_FOUND_MESSAGE,
    LESSON_UPDATED_SUCCESS_MESSAGE,
)

lesson_mapper = LessonMapper()


def handle_get_lessons(handler, lesson_service) -> None:
    lessons = lesson_service.get_all_lessons()

    lesson_responses = [
        lesson_mapper.domain_to_details(lesson).to_camel_dict() for lesson in lessons
    ]

    send_json(
        handler,
        200,
        {
            "success": True,
            "lessons": lesson_responses,
        },
    )


def handle_get_lesson_by_id(handler, lesson_service, path: str) -> None:
    try:
        lesson_id = extract_path_id(path)
        lesson_lookup = lesson_mapper.lesson_id_to_domain(lesson_id)

        lesson = lesson_service.get_lesson_by_id(lesson_lookup)

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

    if lesson is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": LESSON_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "lesson": lesson_mapper.domain_to_details(lesson).to_camel_dict(),
        },
    )


def handle_create_lesson(handler, lesson_service) -> None:
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
        create_request = CreateLessonRequest(
            category_id=int(request_data.get("category_id", 0)),
            lesson_type_id=int(request_data.get("lesson_type_id", 0)),
            embodiment_type_id=int(request_data.get("embodiment_type_id", 0)),
            interaction_style_id=int(request_data.get("interaction_style_id", 0)),
            title=request_data.get("title", ""),
            description=request_data.get("description"),
            is_active=bool(request_data.get("is_active", True)),
            updated_by=request_data.get("updated_by"),
        )

        lesson = lesson_mapper.create_request_to_domain(create_request)

        created_lesson = lesson_service.create_lesson(lesson)

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
            "message": LESSON_CREATED_SUCCESS_MESSAGE,
            "lesson": lesson_mapper.domain_to_details(created_lesson).to_camel_dict(),
        },
    )


def handle_update_lesson(handler, lesson_service, path: str) -> None:
    try:
        lesson_id = extract_path_id(path)

    except ValueError:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_LESSON_ID_MESSAGE,
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
        update_request = UpdateLessonRequest(
            lesson_id=lesson_id,
            category_id=int(request_data.get("category_id", 0)),
            lesson_type_id=int(request_data.get("lesson_type_id", 0)),
            embodiment_type_id=int(request_data.get("embodiment_type_id", 0)),
            interaction_style_id=int(request_data.get("interaction_style_id", 0)),
            title=request_data.get("title", ""),
            description=request_data.get("description"),
            is_active=bool(request_data.get("is_active", False)),
            updated_by=request_data.get("updated_by"),
        )

        lesson = lesson_mapper.update_request_to_domain(update_request)

        updated_lesson = lesson_service.update_lesson(lesson)

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

    if updated_lesson is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": LESSON_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": LESSON_UPDATED_SUCCESS_MESSAGE,
            "lesson": lesson_mapper.domain_to_details(updated_lesson).to_camel_dict(),
        },
    )


def handle_delete_lesson(handler, lesson_service, path: str) -> None:
    try:
        lesson_id = extract_path_id(path)
        lesson = lesson_mapper.lesson_id_to_domain(lesson_id)

        was_deleted = lesson_service.delete_lesson(lesson)

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
                "error": LESSON_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": LESSON_DELETED_SUCCESS_MESSAGE,
        },
    )
