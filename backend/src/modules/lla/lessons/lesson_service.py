"""
Lesson application service.

Responsibilities:
- Coordinate lesson CRUD use cases.
- Keep API handlers separate from repository/database details.
- Delegate lesson validation to the lesson validator.
- Work with lesson domain objects only.

Architecture:
API -> Mapper -> LessonService -> LessonValidator -> LessonRepository -> SQLite Database
"""

from src.modules.lla.lessons.lesson import Lesson


class LessonService:
    def __init__(
        self,
        lesson_repository,
        lesson_validator,
    ):
        self.lesson_repository = lesson_repository
        self.lesson_validator = lesson_validator

    def get_all_lessons(self) -> list[Lesson]:
        return self.lesson_repository.find_all_lessons()

    def get_lesson_by_id(
        self,
        lesson: Lesson,
    ) -> Lesson | None:
        self.lesson_validator.validate_lesson_id(lesson)

        return self.lesson_repository.find_by_id(lesson)

    def create_lesson(
        self,
        lesson: Lesson,
    ) -> Lesson:
        self.lesson_validator.validate_create_lesson(lesson)

        return self.lesson_repository.create_lesson(lesson)

    def update_lesson(
        self,
        lesson: Lesson,
    ) -> Lesson | None:
        self.lesson_validator.validate_update_lesson(lesson)

        return self.lesson_repository.update_lesson(lesson)

    def delete_lesson(
        self,
        lesson: Lesson,
    ) -> bool:
        self.lesson_validator.validate_lesson_id(lesson)

        return self.lesson_repository.delete_lesson(lesson)
