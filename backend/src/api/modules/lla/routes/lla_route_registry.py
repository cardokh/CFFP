"""
LLA API route registry builder.

Responsibilities:
- Build route registrations owned by the LLA module.
- Keep LLA route-handler wiring close to the LLA API route modules.
- Keep the central route registry smaller and focused on application-level composition.
- Inject LLA services explicitly into route handlers.

Architecture:
app.py -> route_registry -> LLA route registry -> route_dispatcher -> LLA route handlers
"""

from src.api.http_methods import (
    HTTP_METHOD_DELETE,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
)
from src.api.modules.lla.lla_api_paths import (
    API_PATH_ADMIN_LEARNING_ITEM_EXAMPLES_PREFIX,
    API_PATH_ADMIN_LEARNING_ITEMS,
    API_PATH_ADMIN_LEARNING_ITEMS_PREFIX,
    API_PATH_ADMIN_LESSON_CATEGORIES,
    API_PATH_ADMIN_LESSON_CATEGORIES_PREFIX,
    API_PATH_ADMIN_LESSON_FORM_OPTIONS,
    API_PATH_ADMIN_LESSON_LEARNING_ITEMS_PREFIX,
    API_PATH_ADMIN_LESSON_QUIZ_QUESTIONS_PREFIX,
    API_PATH_ADMIN_LESSONS,
    API_PATH_ADMIN_LESSONS_PREFIX,
    API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS,
    API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS_BY_QUESTION_PREFIX,
    API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS_PREFIX,
    API_PATH_ADMIN_QUIZ_QUESTIONS,
    API_PATH_ADMIN_QUIZ_QUESTIONS_PREFIX,
    API_PATH_ADMIN_USER_LESSONS_COMPLETED_PREFIX,
    API_PATH_ADMIN_USER_LESSONS_IN_PROGRESS_PREFIX,
    API_PATH_ADMIN_USER_LESSONS_PREFIX,
    API_PATH_LESSON_INTERACTION,
    API_PATH_STUDENT_LESSONS_PREFIX,
    API_PATH_STUDENT_LESSONS_REMOVE_PREFIX,
    API_PATH_STUDENT_LESSONS_SIGNUP_PREFIX,
    API_PATH_STUDENT_PROGRESS_PREFIX,
    API_PATH_TTS_PREFIX,
)
from src.api.route_dispatcher import RouteRegistry
from src.modules.lla.learning_items.learning_item_routes import (
    handle_create_learning_item,
    handle_delete_learning_item,
    handle_generate_learning_item_examples,
    handle_get_learning_item_by_id,
    handle_get_learning_items,
    handle_update_learning_item,
)
from src.modules.lla.lesson_categories.lesson_category_routes import (
    handle_create_lesson_category,
    handle_delete_lesson_category,
    handle_get_lesson_categories,
    handle_get_lesson_category_by_id,
    handle_update_lesson_category,
)
from src.modules.lla.lessons.lesson_interaction_routes import (
    handle_get_lesson_phrase,
    handle_text_to_speech,
)
from src.modules.lla.lessons.lesson_learning_item_assignment_routes import (
    handle_get_lesson_learning_items,
    handle_replace_lesson_learning_items,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_routes import (
    handle_get_lesson_quiz_questions,
    handle_replace_lesson_quiz_questions,
)
from src.modules.lla.lessons.lesson_routes import (
    handle_create_lesson,
    handle_delete_lesson,
    handle_get_lesson_by_id,
    handle_get_lessons,
    handle_update_lesson,
)
from src.modules.lla.quiz_questions.quiz_question_option_routes import (
    handle_create_quiz_question_option,
    handle_delete_quiz_question_option,
    handle_get_quiz_question_options,
    handle_replace_quiz_question_options,
    handle_update_quiz_question_option,
)
from src.modules.lla.quiz_questions.quiz_question_routes import (
    handle_create_quiz_question,
    handle_delete_quiz_question,
    handle_get_quiz_question_by_id,
    handle_get_quiz_questions,
    handle_update_quiz_question,
)
from src.modules.lla.reference_data.reference_data_routes import (
    handle_get_lesson_form_options,
)
from src.modules.lla.user_lesson_assignments.user_lesson_assignment_routes import (
    handle_get_student_lessons,
    handle_get_user_lesson_assignments,
    handle_mark_lesson_completed,
    handle_mark_lesson_in_progress,
    handle_remove_student_lesson,
    handle_replace_user_lesson_assignments,
    handle_signup_student_lesson,
)
from src.modules.lla.student_progress.student_progress_routes import (
    handle_get_student_progress,
)


def build_lla_route_registry(
    handler,
    services,
) -> RouteRegistry:
    return {
        HTTP_METHOD_GET: {
            "exact": {
                API_PATH_ADMIN_LESSON_FORM_OPTIONS: lambda: handle_get_lesson_form_options(
                    handler,
                    services.reference_data_service,
                ),
                API_PATH_ADMIN_LESSON_CATEGORIES: lambda: handle_get_lesson_categories(
                    handler,
                    services.lesson_category_service,
                ),
                API_PATH_ADMIN_LEARNING_ITEMS: lambda: handle_get_learning_items(
                    handler,
                    services.learning_item_service,
                ),
                API_PATH_ADMIN_QUIZ_QUESTIONS: lambda: handle_get_quiz_questions(
                    handler,
                    services.quiz_question_service,
                ),
                API_PATH_ADMIN_LESSONS: lambda: handle_get_lessons(
                    handler,
                    services.lesson_service,
                ),
                API_PATH_LESSON_INTERACTION: lambda: handle_get_lesson_phrase(handler),
            },
            "prefix": {
                API_PATH_ADMIN_LESSON_CATEGORIES_PREFIX: lambda path: handle_get_lesson_category_by_id(
                    handler,
                    services.lesson_category_service,
                    path,
                ),
                API_PATH_ADMIN_LEARNING_ITEM_EXAMPLES_PREFIX: lambda path: handle_generate_learning_item_examples(
                    handler,
                    services.learning_item_service,
                    path,
                ),
                API_PATH_ADMIN_LEARNING_ITEMS_PREFIX: lambda path: handle_get_learning_item_by_id(
                    handler,
                    services.learning_item_service,
                    path,
                ),
                API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS_BY_QUESTION_PREFIX: lambda path: handle_get_quiz_question_options(
                    handler,
                    services.quiz_question_option_service,
                    path,
                ),
                API_PATH_ADMIN_QUIZ_QUESTIONS_PREFIX: lambda path: handle_get_quiz_question_by_id(
                    handler,
                    services.quiz_question_service,
                    services.quiz_question_option_service,
                    path,
                ),
                API_PATH_ADMIN_LESSONS_PREFIX: lambda path: handle_get_lesson_by_id(
                    handler,
                    services.lesson_service,
                    path,
                ),
                API_PATH_ADMIN_LESSON_LEARNING_ITEMS_PREFIX: lambda path: handle_get_lesson_learning_items(
                    handler,
                    services.lesson_learning_item_assignment_service,
                    path,
                ),
                API_PATH_ADMIN_LESSON_QUIZ_QUESTIONS_PREFIX: lambda path: handle_get_lesson_quiz_questions(
                    handler,
                    services.lesson_quiz_question_assignment_service,
                    path,
                ),
                API_PATH_ADMIN_USER_LESSONS_PREFIX: lambda path: handle_get_user_lesson_assignments(
                    handler,
                    services.user_lesson_assignment_service,
                    path,
                ),
                API_PATH_STUDENT_LESSONS_PREFIX: lambda path: handle_get_student_lessons(
                    handler,
                    services.user_lesson_assignment_service,
                    path,
                ),
                API_PATH_STUDENT_PROGRESS_PREFIX: lambda path: handle_get_student_progress(
                    handler,
                    services.student_progress_service,
                    path,
                ),
                API_PATH_TTS_PREFIX: lambda path: handle_text_to_speech(handler),
            },
        },
        HTTP_METHOD_POST: {
            "exact": {
                API_PATH_ADMIN_LESSON_CATEGORIES: lambda: handle_create_lesson_category(
                    handler,
                    services.lesson_category_service,
                ),
                API_PATH_ADMIN_LEARNING_ITEMS: lambda: handle_create_learning_item(
                    handler,
                    services.learning_item_service,
                ),
                API_PATH_ADMIN_QUIZ_QUESTIONS: lambda: handle_create_quiz_question(
                    handler,
                    services.quiz_question_service,
                ),
                API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS: lambda: handle_create_quiz_question_option(
                    handler,
                    services.quiz_question_option_service,
                ),
                API_PATH_ADMIN_LESSONS: lambda: handle_create_lesson(
                    handler,
                    services.lesson_service,
                ),
            },
            "prefix": {
                API_PATH_ADMIN_USER_LESSONS_IN_PROGRESS_PREFIX: lambda path: handle_mark_lesson_in_progress(
                    handler,
                    services.user_lesson_assignment_service,
                    path,
                ),
                API_PATH_ADMIN_USER_LESSONS_COMPLETED_PREFIX: lambda path: handle_mark_lesson_completed(
                    handler,
                    services.user_lesson_assignment_service,
                    path,
                ),
                API_PATH_STUDENT_LESSONS_SIGNUP_PREFIX: lambda path: handle_signup_student_lesson(
                    handler,
                    services.user_lesson_assignment_service,
                    path,
                ),
            },
        },
        HTTP_METHOD_PUT: {
            "prefix": {
                API_PATH_ADMIN_LESSON_CATEGORIES_PREFIX: lambda path: handle_update_lesson_category(
                    handler,
                    services.lesson_category_service,
                    path,
                ),
                API_PATH_ADMIN_LEARNING_ITEMS_PREFIX: lambda path: handle_update_learning_item(
                    handler,
                    services.learning_item_service,
                    path,
                ),
                API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS_BY_QUESTION_PREFIX: lambda path: handle_replace_quiz_question_options(
                    handler,
                    services.quiz_question_option_service,
                    path,
                ),
                API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS_PREFIX: lambda path: handle_update_quiz_question_option(
                    handler,
                    services.quiz_question_option_service,
                    path,
                ),
                API_PATH_ADMIN_QUIZ_QUESTIONS_PREFIX: lambda path: handle_update_quiz_question(
                    handler,
                    services.quiz_question_service,
                    path,
                ),
                API_PATH_ADMIN_LESSONS_PREFIX: lambda path: handle_update_lesson(
                    handler,
                    services.lesson_service,
                    path,
                ),
                API_PATH_ADMIN_LESSON_LEARNING_ITEMS_PREFIX: lambda path: handle_replace_lesson_learning_items(
                    handler,
                    services.lesson_learning_item_assignment_service,
                    path,
                ),
                API_PATH_ADMIN_LESSON_QUIZ_QUESTIONS_PREFIX: lambda path: handle_replace_lesson_quiz_questions(
                    handler,
                    services.lesson_quiz_question_assignment_service,
                    path,
                ),
                API_PATH_ADMIN_USER_LESSONS_PREFIX: lambda path: handle_replace_user_lesson_assignments(
                    handler,
                    services.user_lesson_assignment_service,
                    path,
                ),
            },
        },
        HTTP_METHOD_DELETE: {
            "prefix": {
                API_PATH_ADMIN_LESSON_CATEGORIES_PREFIX: lambda path: handle_delete_lesson_category(
                    handler,
                    services.lesson_category_service,
                    path,
                ),
                API_PATH_ADMIN_LEARNING_ITEMS_PREFIX: lambda path: handle_delete_learning_item(
                    handler,
                    services.learning_item_service,
                    path,
                ),
                API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS_PREFIX: lambda path: handle_delete_quiz_question_option(
                    handler,
                    services.quiz_question_option_service,
                    path,
                ),
                API_PATH_ADMIN_QUIZ_QUESTIONS_PREFIX: lambda path: handle_delete_quiz_question(
                    handler,
                    services.quiz_question_service,
                    path,
                ),
                API_PATH_ADMIN_LESSONS_PREFIX: lambda path: handle_delete_lesson(
                    handler,
                    services.lesson_service,
                    path,
                ),
                API_PATH_STUDENT_LESSONS_REMOVE_PREFIX: lambda path: handle_remove_student_lesson(
                    handler,
                    services.user_lesson_assignment_service,
                    path,
                ),
            },
        },
    }
