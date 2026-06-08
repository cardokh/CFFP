"""
Lesson category application service.

Responsibilities:
- Coordinate lesson category CRUD use cases.
- Keep API handlers separate from repository/database details.
- Delegate lesson category validation to the lesson category validator.
- Work with lesson category domain objects only.

Architecture:
API -> Mapper -> LessonCategoryService -> LessonCategoryValidator -> LessonCategoryRepository -> SQLite Database
"""

from src.modules.lla.lesson_categories.lesson_category import LessonCategory


class LessonCategoryService:
    def __init__(
        self,
        lesson_category_repository,
        lesson_category_validator,
    ):
        self.lesson_category_repository = lesson_category_repository
        self.lesson_category_validator = lesson_category_validator

    def get_all_lesson_categories(self) -> list[LessonCategory]:
        return self.lesson_category_repository.find_all_lesson_categories()

    def get_lesson_category_by_id(
        self,
        lesson_category: LessonCategory,
    ) -> LessonCategory | None:
        self.lesson_category_validator.validate_lesson_category_id(lesson_category)

        return self.lesson_category_repository.find_by_id(lesson_category)

    def create_lesson_category(
        self,
        lesson_category: LessonCategory,
    ) -> LessonCategory:
        self.lesson_category_validator.validate_create_lesson_category(lesson_category)

        return self.lesson_category_repository.create_lesson_category(lesson_category)

    def update_lesson_category(
        self,
        lesson_category: LessonCategory,
    ) -> LessonCategory | None:
        self.lesson_category_validator.validate_update_lesson_category(lesson_category)

        return self.lesson_category_repository.update_lesson_category(lesson_category)

    def delete_lesson_category(
        self,
        lesson_category: LessonCategory,
    ) -> bool:
        self.lesson_category_validator.validate_lesson_category_id(lesson_category)

        return self.lesson_category_repository.delete_lesson_category(lesson_category)
