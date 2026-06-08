"""
LLA module API path constants.

Responsibilities:
- Centralize API route/path strings owned by the LLA module.
- Avoid hardcoded LLA endpoint paths inside route modules.
- Keep LLA-specific API concerns separated from platform/core API paths.

Architecture:
LLA route modules -> lla_api_paths
LLA route registries -> lla_api_paths
"""

API_PATH_TTS_PREFIX = "/api/tts"
API_PATH_LESSON_INTERACTION = "/api/lesson"

API_PATH_ADMIN_LESSON_CATEGORIES = "/api/admin/lesson-categories"
API_PATH_ADMIN_LESSON_CATEGORIES_PREFIX = "/api/admin/lesson-categories/"

API_PATH_ADMIN_LEARNING_ITEMS = "/api/admin/learning-items"
API_PATH_ADMIN_LEARNING_ITEMS_PREFIX = "/api/admin/learning-items/"
API_PATH_ADMIN_LEARNING_ITEM_EXAMPLES_PREFIX = "/api/admin/learning-items/examples/"

API_PATH_ADMIN_QUIZ_QUESTIONS = "/api/admin/quiz-questions"
API_PATH_ADMIN_QUIZ_QUESTIONS_PREFIX = "/api/admin/quiz-questions/"

API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS = "/api/admin/quiz-question-options"

API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS_PREFIX = "/api/admin/quiz-question-options/"

API_PATH_ADMIN_QUIZ_QUESTION_OPTIONS_BY_QUESTION_PREFIX = (
    "/api/admin/quiz-questions-options/"
)

API_PATH_ADMIN_LESSONS = "/api/admin/lessons"
API_PATH_ADMIN_LESSONS_PREFIX = "/api/admin/lessons/"

API_PATH_ADMIN_LESSON_LEARNING_ITEMS_PREFIX = "/api/admin/lessons-learning-items/"

API_PATH_ADMIN_LESSON_QUIZ_QUESTIONS_PREFIX = "/api/admin/lessons-quiz-questions/"

API_PATH_ADMIN_LESSON_FORM_OPTIONS = "/api/admin/reference-data/lesson-form-options"

API_PATH_ADMIN_USER_LESSONS = "/api/admin/user-lessons"

API_PATH_ADMIN_USER_LESSONS_PREFIX = "/api/admin/user-lessons/"

API_PATH_ADMIN_USER_LESSONS_IN_PROGRESS_PREFIX = "/api/admin/user-lessons/in-progress/"

API_PATH_ADMIN_USER_LESSONS_COMPLETED_PREFIX = "/api/admin/user-lessons/completed/"

API_PATH_STUDENT_LESSONS_PREFIX = "/api/student/lessons/"

API_PATH_STUDENT_LESSONS_SIGNUP_PREFIX = "/api/student/lessons/signup/"

API_PATH_STUDENT_LESSONS_REMOVE_PREFIX = "/api/student/lessons/remove/"

API_PATH_STUDENT_PROGRESS_PREFIX = "/api/student/progress/"
