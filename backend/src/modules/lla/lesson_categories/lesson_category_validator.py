"""
Lesson category validation.

Responsibilities:
- Validate lesson category business rules.
- Keep validation concerns separate from service orchestration.
- Validate lesson category domain objects only.

Architecture:
Service -> Validator -> Repository
"""

from src.modules.lla.lesson_categories.lesson_category import LessonCategory
from src.modules.lla.lesson_categories.lesson_category_messages import (
    CATEGORY_NAME_REQUIRED_MESSAGE,
    DUPLICATE_CATEGORY_NAME_MESSAGE,
    INVALID_CATEGORY_ID_MESSAGE,
)


class LessonCategoryValidator:
    def __init__(self, lesson_category_repository):
        self.lesson_category_repository = lesson_category_repository

    def validate_create_lesson_category(
        self,
        lesson_category: LessonCategory,
    ):
        if not lesson_category.name:
            raise ValueError(CATEGORY_NAME_REQUIRED_MESSAGE)

        existing_category = self.lesson_category_repository.find_by_name(
            lesson_category
        )

        if existing_category is not None:
            raise ValueError(DUPLICATE_CATEGORY_NAME_MESSAGE)

    def validate_update_lesson_category(
        self,
        lesson_category: LessonCategory,
    ):
        self.validate_lesson_category_id(lesson_category)

        if not lesson_category.name:
            raise ValueError(CATEGORY_NAME_REQUIRED_MESSAGE)

        existing_category_with_name = self.lesson_category_repository.find_by_name(
            lesson_category
        )

        if (
            existing_category_with_name is not None
            and existing_category_with_name.category_id != lesson_category.category_id
        ):
            raise ValueError(DUPLICATE_CATEGORY_NAME_MESSAGE)

    @staticmethod
    def validate_lesson_category_id(lesson_category: LessonCategory):
        if lesson_category.category_id is None or lesson_category.category_id <= 0:
            raise ValueError(INVALID_CATEGORY_ID_MESSAGE)
