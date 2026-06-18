"""
Application service container.

Responsibilities:
- Centralize construction and ownership of application services.
- Keep API request handlers independent from service construction details.
- Provide one shared access point for services used by route handlers.

Architecture:
app.py -> service_container -> services -> repositories -> SQLite
"""

from types import SimpleNamespace

from src.core.application.service_factory import (
    build_ai_speech_service,
    build_automation_pipeline_service,
    build_automation_task_service,
    build_ai_speech_validator,
    build_learning_item_service,
    build_lesson_category_service,
    build_lesson_learning_item_assignment_service,
    build_lesson_quiz_question_assignment_service,
    build_lesson_service,
    build_quiz_question_option_service,
    build_quiz_question_service,
    build_reference_data_service,
    build_user_lesson_assignment_service,
    build_users_service,
    build_student_progress_service,
)


def build_service_container() -> SimpleNamespace:
    """
    Build and return the application service container.

    All application services should be constructed here so route handlers receive
    explicit dependencies from the route registry instead of constructing services
    themselves or resolving them indirectly through the HTTP handler.
    """
    return SimpleNamespace(
        users_service=build_users_service(),
        lesson_category_service=build_lesson_category_service(),
        learning_item_service=build_learning_item_service(),
        quiz_question_service=build_quiz_question_service(),
        quiz_question_option_service=build_quiz_question_option_service(),
        lesson_service=build_lesson_service(),
        lesson_learning_item_assignment_service=build_lesson_learning_item_assignment_service(),
        lesson_quiz_question_assignment_service=build_lesson_quiz_question_assignment_service(),
        user_lesson_assignment_service=build_user_lesson_assignment_service(),
        student_progress_service=build_student_progress_service(),
        reference_data_service=build_reference_data_service(),
        ai_speech_service=build_ai_speech_service(),
        ai_speech_validator=build_ai_speech_validator(),
        automation_task_service=build_automation_task_service(),
        automation_pipeline_service=build_automation_pipeline_service(),
    )
