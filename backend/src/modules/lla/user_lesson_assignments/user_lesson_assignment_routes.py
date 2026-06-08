"""
User lesson assignment routes.

Responsibilities:
- Handle HTTP requests for user lesson assignments.
- Validate request payloads before mapping.
- Convert route/path/body data into request DTOs through the mapper.
- Delegate business logic to the service layer.
- Return consistent JSON API responses.

Architecture:
HTTP -> routes -> validator/mapper/contracts -> service -> repository
"""

from src.api.route_utils import (
    extract_path_id,
    read_json_body,
    send_json,
)

from src.modules.lla.user_lesson_assignments.user_lesson_assignment_mapper import (
    UserLessonAssignmentMapper,
)

from src.modules.lla.user_lesson_assignments.user_lesson_assignment_messages import (
    STUDENT_LESSONS_FETCHED_SUCCESSFULLY,
    STUDENT_LESSON_REMOVED_SUCCESSFULLY,
    STUDENT_LESSON_SIGNUP_SUCCESSFUL,
    USER_LESSON_ASSIGNMENTS_FETCHED_SUCCESSFULLY,
    USER_LESSON_ASSIGNMENTS_UPDATED_SUCCESSFULLY,
)

from src.modules.lla.user_lesson_assignments.user_lesson_assignment_validator import (
    UserLessonAssignmentValidator,
)


def handle_get_user_lesson_assignments(
    handler,
    user_lesson_assignment_service,
    path,
):
    try:
        user_id = extract_path_id(path)

        request = UserLessonAssignmentMapper.get_request_from_user_id(user_id)

        assignments = user_lesson_assignment_service.get_user_lesson_assignments(
            request
        )

        assignment_dicts = UserLessonAssignmentMapper.to_response_dict_list(assignments)

        send_json(
            handler,
            200,
            {
                "success": True,
                "message": USER_LESSON_ASSIGNMENTS_FETCHED_SUCCESSFULLY,
                "userLessons": assignment_dicts,
            },
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


def handle_replace_user_lesson_assignments(
    handler,
    user_lesson_assignment_service,
    path,
):
    try:
        user_id = extract_path_id(path)

        request_data = read_json_body(handler)

        if request_data is None:
            send_json(
                handler,
                400,
                {
                    "success": False,
                    "error": "Invalid JSON body",
                },
            )

            return

        UserLessonAssignmentValidator.validate_assignment_payload(request_data)

        request = UserLessonAssignmentMapper.replace_request_from_payload(
            user_id,
            request_data,
        )

        assignments = user_lesson_assignment_service.replace_user_lesson_assignments(
            request
        )

        assignment_dicts = UserLessonAssignmentMapper.to_response_dict_list(assignments)

        send_json(
            handler,
            200,
            {
                "success": True,
                "message": USER_LESSON_ASSIGNMENTS_UPDATED_SUCCESSFULLY,
                "userLessons": assignment_dicts,
            },
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


def handle_mark_lesson_in_progress(
    handler,
    user_lesson_assignment_service,
    path,
):
    try:
        user_id = extract_path_id(path)

        request_data = read_json_body(handler)

        if request_data is None:
            send_json(
                handler,
                400,
                {
                    "success": False,
                    "error": "Invalid JSON body",
                },
            )

            return

        UserLessonAssignmentValidator.validate_status_update_payload(request_data)

        lesson_id = request_data.get("lesson_id")

        request = UserLessonAssignmentMapper.status_update_request_from_ids(
            user_id,
            lesson_id,
        )

        assignments = user_lesson_assignment_service.mark_lesson_in_progress(request)

        assignment_dicts = UserLessonAssignmentMapper.to_response_dict_list(assignments)

        send_json(
            handler,
            200,
            {
                "success": True,
                "message": USER_LESSON_ASSIGNMENTS_UPDATED_SUCCESSFULLY,
                "userLessons": assignment_dicts,
            },
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


def handle_mark_lesson_completed(
    handler,
    user_lesson_assignment_service,
    path,
):
    try:
        user_id = extract_path_id(path)

        request_data = read_json_body(handler)

        if request_data is None:
            send_json(
                handler,
                400,
                {
                    "success": False,
                    "error": "Invalid JSON body",
                },
            )

            return

        UserLessonAssignmentValidator.validate_status_update_payload(request_data)

        request = UserLessonAssignmentMapper.status_update_request_from_payload(
            user_id,
            request_data,
        )

        assignments = user_lesson_assignment_service.mark_lesson_completed(request)

        assignment_dicts = UserLessonAssignmentMapper.to_response_dict_list(assignments)

        send_json(
            handler,
            200,
            {
                "success": True,
                "message": USER_LESSON_ASSIGNMENTS_UPDATED_SUCCESSFULLY,
                "userLessons": assignment_dicts,
            },
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


def handle_get_student_lessons(
    handler,
    user_lesson_assignment_service,
    path,
):
    try:
        user_id = extract_path_id(path)

        request = UserLessonAssignmentMapper.get_request_from_user_id(user_id)

        assignments = user_lesson_assignment_service.get_student_lessons(request)

        assignment_dicts = UserLessonAssignmentMapper.to_response_dict_list(assignments)

        send_json(
            handler,
            200,
            {
                "success": True,
                "message": STUDENT_LESSONS_FETCHED_SUCCESSFULLY,
                "userLessons": assignment_dicts,
            },
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


def handle_signup_student_lesson(
    handler,
    user_lesson_assignment_service,
    path,
):
    try:
        user_id = extract_path_id(path)

        request_data = read_json_body(handler)

        if request_data is None:
            send_json(
                handler,
                400,
                {
                    "success": False,
                    "error": "Invalid JSON body",
                },
            )

            return

        UserLessonAssignmentValidator.validate_student_lesson_signup_payload(
            request_data
        )

        lesson_id = request_data.get("lesson_id")

        request = UserLessonAssignmentMapper.signup_student_lesson_request_from_ids(
            user_id,
            lesson_id,
        )

        assignments = user_lesson_assignment_service.signup_student_lesson(request)

        assignment_dicts = UserLessonAssignmentMapper.to_response_dict_list(assignments)

        send_json(
            handler,
            200,
            {
                "success": True,
                "message": STUDENT_LESSON_SIGNUP_SUCCESSFUL,
                "userLessons": assignment_dicts,
            },
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


def handle_remove_student_lesson(
    handler,
    user_lesson_assignment_service,
    path,
):
    try:
        user_id = extract_path_id(path)

        request_data = read_json_body(handler)

        if request_data is None:
            send_json(
                handler,
                400,
                {
                    "success": False,
                    "error": "Invalid JSON body",
                },
            )

            return

        UserLessonAssignmentValidator.validate_student_lesson_remove_payload(
            request_data
        )

        lesson_id = request_data.get("lesson_id")

        request = UserLessonAssignmentMapper.remove_student_lesson_request_from_ids(
            user_id,
            lesson_id,
        )

        assignments = user_lesson_assignment_service.remove_student_lesson(request)

        assignment_dicts = UserLessonAssignmentMapper.to_response_dict_list(assignments)

        send_json(
            handler,
            200,
            {
                "success": True,
                "message": STUDENT_LESSON_REMOVED_SUCCESSFULLY,
                "userLessons": assignment_dicts,
            },
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
