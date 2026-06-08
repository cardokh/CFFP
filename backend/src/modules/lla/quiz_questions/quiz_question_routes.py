"""
Quiz question API routes.

Responsibilities:
- Handle quiz question CRUD route actions.
- Keep quiz question endpoint logic out of app.py.
- Convert HTTP/JSON request data into quiz question request contracts.
- Use mapper to convert request contracts into domain objects.
- Delegate domain-level CRUD use cases to QuizQuestionService.
- Convert returned domain objects into API-friendly response structures.
- Include quiz question options in detail responses.
- Return consistent JSON API responses.

Architecture:
app.py -> route_registry -> quiz_question_routes -> request contract
-> QuizQuestionMapper -> QuizQuestionService -> QuizQuestionValidator
-> QuizQuestionRepository -> SQLite

Note:
Quiz question options are loaded through QuizQuestionOptionService.
"""

from src.api.route_utils import (
    extract_path_id,
    read_json_body,
    send_json,
)
from src.modules.lla.quiz_questions.quiz_question_contracts import (
    CreateQuizQuestionRequest,
    UpdateQuizQuestionRequest,
)
from src.modules.lla.quiz_questions.quiz_question_mapper import (
    QuizQuestionMapper,
)
from src.modules.lla.quiz_questions.quiz_question_messages import (
    INVALID_JSON_BODY_MESSAGE,
    INVALID_QUIZ_QUESTION_ID_MESSAGE,
    QUIZ_QUESTION_CREATED_SUCCESS_MESSAGE,
    QUIZ_QUESTION_DELETED_SUCCESS_MESSAGE,
    QUIZ_QUESTION_NOT_FOUND_MESSAGE,
    QUIZ_QUESTION_UPDATED_SUCCESS_MESSAGE,
)

quiz_question_mapper = QuizQuestionMapper()


def handle_get_quiz_questions(handler, quiz_question_service) -> None:
    quiz_questions = quiz_question_service.get_all_quiz_questions()

    quiz_question_responses = [
        quiz_question_mapper.domain_to_details(quiz_question).to_dict()
        for quiz_question in quiz_questions
    ]

    send_json(
        handler,
        200,
        {
            "success": True,
            "quizQuestions": quiz_question_responses,
        },
    )


def handle_get_quiz_question_by_id(
    handler,
    quiz_question_service,
    quiz_question_option_service,
    path: str,
) -> None:
    try:
        question_id = extract_path_id(path)
        quiz_question_lookup = quiz_question_mapper.question_id_to_domain(question_id)

        quiz_question = quiz_question_service.get_quiz_question_by_id(
            quiz_question_lookup
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

    if quiz_question is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": QUIZ_QUESTION_NOT_FOUND_MESSAGE,
            },
        )
        return

    quiz_question_options = quiz_question_option_service.get_options_by_question_id(
        question_id
    )

    send_json(
        handler,
        200,
        {
            "success": True,
            "quizQuestion": quiz_question_mapper.domain_to_details(
                quiz_question,
                quiz_question_options,
            ).to_dict(),
        },
    )


def handle_create_quiz_question(handler, quiz_question_service) -> None:
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
        create_request = CreateQuizQuestionRequest(
            category_id=int(request_data.get("categoryId", 0)),
            question_text=request_data.get("questionText", ""),
            is_active=bool(request_data.get("isActive", True)),
            updated_by=request_data.get("updatedBy"),
        )

        quiz_question = quiz_question_mapper.create_request_to_domain(create_request)

        created_question = quiz_question_service.create_quiz_question(quiz_question)

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
            "message": QUIZ_QUESTION_CREATED_SUCCESS_MESSAGE,
            "quizQuestion": quiz_question_mapper.domain_to_details(
                created_question
            ).to_dict(),
        },
    )


def handle_update_quiz_question(
    handler,
    quiz_question_service,
    path: str,
) -> None:
    try:
        question_id = extract_path_id(path)

    except ValueError:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_QUIZ_QUESTION_ID_MESSAGE,
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
        update_request = UpdateQuizQuestionRequest(
            question_id=question_id,
            category_id=int(request_data.get("categoryId", 0)),
            question_text=request_data.get("questionText", ""),
            is_active=bool(request_data.get("isActive", False)),
            updated_by=request_data.get("updatedBy"),
        )

        quiz_question = quiz_question_mapper.update_request_to_domain(update_request)

        updated_question = quiz_question_service.update_quiz_question(quiz_question)

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

    if updated_question is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": QUIZ_QUESTION_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": QUIZ_QUESTION_UPDATED_SUCCESS_MESSAGE,
            "quizQuestion": quiz_question_mapper.domain_to_details(
                updated_question
            ).to_dict(),
        },
    )


def handle_delete_quiz_question(
    handler,
    quiz_question_service,
    path: str,
) -> None:
    try:
        question_id = extract_path_id(path)
        quiz_question = quiz_question_mapper.question_id_to_domain(question_id)

        was_deleted = quiz_question_service.delete_quiz_question(quiz_question)

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
                "error": QUIZ_QUESTION_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": QUIZ_QUESTION_DELETED_SUCCESS_MESSAGE,
        },
    )
