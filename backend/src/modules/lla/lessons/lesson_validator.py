"""
Lesson validation.

Responsibilities:
- Validate lesson business rules.
- Keep validation concerns separate from service orchestration.
- Validate lesson domain objects only.

Architecture:
Service -> Validator -> Repository
"""

from src.modules.lla.lessons.lesson import Lesson
from src.modules.lla.lessons.lesson_messages import (
    INVALID_CATEGORY_ID_MESSAGE,
    INVALID_EMBODIMENT_TYPE_ID_MESSAGE,
    INVALID_INTERACTION_STYLE_ID_MESSAGE,
    INVALID_LESSON_ID_MESSAGE,
    INVALID_LESSON_TYPE_ID_MESSAGE,
    LESSON_TITLE_REQUIRED_MESSAGE,
)


class LessonValidator:
    @staticmethod
    def validate_lesson_id(lesson: Lesson):
        if lesson.lesson_id is None or lesson.lesson_id <= 0:
            raise ValueError(INVALID_LESSON_ID_MESSAGE)

    def validate_create_lesson(
        self,
        lesson: Lesson,
    ):
        self._validate_lesson_fields(lesson)

    def validate_update_lesson(
        self,
        lesson: Lesson,
    ):
        self.validate_lesson_id(lesson)
        self._validate_lesson_fields(lesson)

    @staticmethod
    def _validate_lesson_fields(
        lesson: Lesson,
    ):
        if lesson.category_id is None or lesson.category_id <= 0:
            raise ValueError(INVALID_CATEGORY_ID_MESSAGE)

        if lesson.lesson_type_id is None or lesson.lesson_type_id <= 0:
            raise ValueError(INVALID_LESSON_TYPE_ID_MESSAGE)

        if lesson.embodiment_type_id is None or lesson.embodiment_type_id <= 0:
            raise ValueError(INVALID_EMBODIMENT_TYPE_ID_MESSAGE)

        if lesson.interaction_style_id is None or lesson.interaction_style_id <= 0:
            raise ValueError(INVALID_INTERACTION_STYLE_ID_MESSAGE)

        if not lesson.title:
            raise ValueError(LESSON_TITLE_REQUIRED_MESSAGE)
