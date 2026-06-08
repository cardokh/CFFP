"""
Quiz question option API routes.

Responsibilities:
- Handle quiz question option CRUD route actions.
- Keep quiz question option endpoint logic out of app.py.
- Convert HTTP/JSON request data into quiz question option request contracts.
- Use mapper to convert request contracts into domain objects.
- Delegate domain-level CRUD use cases to QuizQuestionOptionService.
- Convert returned domain objects into API-friendly response structures.
- Support aggregate-style replacement of all options for a quiz question.
- Return consistent JSON API responses.

Architecture:
app.py -> route_registry -> quiz_question_option_routes -> request contract
-> QuizQuestionOptionMapper -> QuizQuestionOptionService
-> QuizQuestionOptionValidator -> QuizQuestionOptionRepository -> SQLite
"""

from src.api.route_utils import (
    extract_path_id,
    extract_path_id_at_index,
    read_json_body,
    send_json,
)
from src.modules.lla.quiz_questions.quiz_question_option_contracts import (
    CreateQuizQuestionOptionRequest,
    UpdateQuizQuestionOptionRequest,
)
from src.modules.lla.quiz_questions.quiz_question_option_mapper import (
    QuizQuestionOptionMapper,
)
from src.modules.lla.quiz_questions.quiz_question_option_messages import (
    INVALID_JSON_BODY_MESSAGE,
    INVALID_QUIZ_QUESTION_ID_MESSAGE,
    INVALID_QUIZ_QUESTION_OPTION_ID_MESSAGE,
    QUIZ_QUESTION_OPTION_CREATED_SUCCESS_MESSAGE,
    QUIZ_QUESTION_OPTION_DELETED_SUCCESS_MESSAGE,
    QUIZ_QUESTION_OPTION_NOT_FOUND_MESSAGE,
    QUIZ_QUESTION_OPTION_UPDATED_SUCCESS_MESSAGE,
    QUIZ_QUESTION_OPTIONS_UPDATED_SUCCESS_MESSAGE,
)

QUIZ_QUESTION_ID_PATH_INDEX = 3

quiz_question_option_mapper = QuizQuestionOptionMapper()


def extract_quiz_question_id_from_options_path(path: str) -> int:
    question_id = extract_path_id_at_index(
        path,
        QUIZ_QUESTION_ID_PATH_INDEX,
    )

    if question_id <= 0:
        raise ValueError(INVALID_QUIZ_QUESTION_ID_MESSAGE)

    return question_id


def handle_get_quiz_question_options(
    handler,
    quiz_question_option_service,
    path: str,
) -> None:
    try:
        question_id = extract_quiz_question_id_from_options_path(path)

        options = quiz_question_option_service.get_options_by_question_id(question_id)

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

    option_responses = [
        quiz_question_option_mapper.domain_to_details(option).to_dict()
        for option in options
    ]

    send_json(
        handler,
        200,
        {
            "success": True,
            "quizQuestionOptions": option_responses,
        },
    )


def handle_create_quiz_question_option(
    handler,
    quiz_question_option_service,
) -> None:
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
        create_request = CreateQuizQuestionOptionRequest(
            question_id=int(request_data.get("questionId", 0)),
            option_text=request_data.get("optionText", ""),
            is_correct=bool(request_data.get("isCorrect", False)),
            display_order=int(request_data.get("displayOrder", 0)),
            updated_by=request_data.get("updatedBy"),
        )

        quiz_question_option = quiz_question_option_mapper.create_request_to_domain(
            create_request
        )

        created_option = quiz_question_option_service.create_quiz_question_option(
            quiz_question_option
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
            "message": QUIZ_QUESTION_OPTION_CREATED_SUCCESS_MESSAGE,
            "quizQuestionOption": quiz_question_option_mapper.domain_to_details(
                created_option
            ).to_dict(),
        },
    )


def handle_update_quiz_question_option(
    handler,
    quiz_question_option_service,
    path: str,
) -> None:
    try:
        option_id = extract_path_id(path)

    except ValueError:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_QUIZ_QUESTION_OPTION_ID_MESSAGE,
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
        update_request = UpdateQuizQuestionOptionRequest(
            option_id=option_id,
            question_id=int(request_data.get("questionId", 0)),
            option_text=request_data.get("optionText", ""),
            is_correct=bool(request_data.get("isCorrect", False)),
            display_order=int(request_data.get("displayOrder", 0)),
            updated_by=request_data.get("updatedBy"),
        )

        quiz_question_option = quiz_question_option_mapper.update_request_to_domain(
            update_request
        )

        updated_option = quiz_question_option_service.update_quiz_question_option(
            quiz_question_option
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

    if updated_option is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": QUIZ_QUESTION_OPTION_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": QUIZ_QUESTION_OPTION_UPDATED_SUCCESS_MESSAGE,
            "quizQuestionOption": quiz_question_option_mapper.domain_to_details(
                updated_option
            ).to_dict(),
        },
    )


def handle_delete_quiz_question_option(
    handler,
    quiz_question_option_service,
    path: str,
) -> None:
    try:
        option_id = extract_path_id(path)

        quiz_question_option = quiz_question_option_mapper.option_id_to_domain(
            option_id
        )

        was_deleted = quiz_question_option_service.delete_quiz_question_option(
            quiz_question_option
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

    if not was_deleted:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": QUIZ_QUESTION_OPTION_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": QUIZ_QUESTION_OPTION_DELETED_SUCCESS_MESSAGE,
        },
    )


def handle_replace_quiz_question_options(
    handler,
    quiz_question_option_service,
    path: str,
) -> None:
    try:
        question_id = extract_quiz_question_id_from_options_path(path)

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
        option_payloads = request_data.get("answerOptions", [])
        updated_by = request_data.get("updatedBy")

        quiz_question_options = []

        for index, option_payload in enumerate(option_payloads, start=1):
            create_request = CreateQuizQuestionOptionRequest(
                question_id=question_id,
                option_text=option_payload.get("optionText", ""),
                is_correct=bool(option_payload.get("isCorrect", False)),
                display_order=index,
                updated_by=updated_by,
            )

            quiz_question_options.append(
                quiz_question_option_mapper.create_request_to_domain(create_request)
            )

        replaced_options = quiz_question_option_service.replace_question_options(
            question_id,
            quiz_question_options,
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

    option_responses = [
        quiz_question_option_mapper.domain_to_details(option).to_dict()
        for option in replaced_options
    ]

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": QUIZ_QUESTION_OPTIONS_UPDATED_SUCCESS_MESSAGE,
            "quizQuestionOptions": option_responses,
        },
    )
