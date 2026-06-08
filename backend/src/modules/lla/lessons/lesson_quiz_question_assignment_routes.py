"""
Lesson quiz question assignment API routes.

Responsibilities:
- Handle lesson quiz question assignment endpoints.
- Convert request payloads into assignment contracts.
- Use mapper/service/validator/repository layers.
"""

from src.api.route_utils import (
    extract_path_id,
    read_json_body,
    send_json,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_contracts import (
    LessonQuizQuestionAssignmentRequest,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_mapper import (
    LessonQuizQuestionAssignmentMapper,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_messages import (
    INVALID_JSON_BODY_MESSAGE,
    LESSON_QUIZ_QUESTIONS_UPDATED_SUCCESS_MESSAGE,
)

assignment_mapper = LessonQuizQuestionAssignmentMapper()


def handle_get_lesson_quiz_questions(
    handler,
    assignment_service,
    path: str,
) -> None:
    try:
        lesson_id = extract_path_id(path)
        assignments = assignment_service.get_assignments_by_lesson_id(lesson_id)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    assignment_responses = [
        assignment_mapper.domain_to_details(assignment).to_camel_dict()
        for assignment in assignments
    ]

    send_json(
        handler,
        200,
        {
            "success": True,
            "lessonQuizQuestions": assignment_responses,
        },
    )


def handle_replace_lesson_quiz_questions(
    handler,
    assignment_service,
    path: str,
) -> None:
    try:
        lesson_id = extract_path_id(path)

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
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
        question_payloads = request_data.get("quiz_questions", [])

        assignments = []

        for index, question_payload in enumerate(question_payloads, start=1):
            request = LessonQuizQuestionAssignmentRequest(
                lesson_id=lesson_id,
                question_id=int(question_payload.get("question_id", 0)),
                display_order=index,
            )

            assignments.append(assignment_mapper.request_to_domain(request))

        replaced_assignments = assignment_service.replace_lesson_quiz_questions(
            lesson_id,
            assignments,
        )

    except ValueError as error:
        send_json(handler, 400, {"success": False, "error": str(error)})
        return

    assignment_responses = [
        assignment_mapper.domain_to_details(assignment).to_camel_dict()
        for assignment in replaced_assignments
    ]

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": LESSON_QUIZ_QUESTIONS_UPDATED_SUCCESS_MESSAGE,
            "lessonQuizQuestions": assignment_responses,
        },
    )
