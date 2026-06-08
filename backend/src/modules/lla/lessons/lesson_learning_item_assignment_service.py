"""
Lesson learning item assignment service.

Responsibilities:
- Coordinate ordered learning item assignment use cases.
- Delegate validation to the assignment validator.
- Work with assignment domain objects only.
"""

from src.modules.lla.lessons.lesson_learning_item_assignment import (
    LessonLearningItemAssignment,
)


class LessonLearningItemAssignmentService:
    def __init__(
        self,
        assignment_repository,
        assignment_validator,
    ):
        self.assignment_repository = assignment_repository
        self.assignment_validator = assignment_validator

    def get_assignments_by_lesson_id(
        self,
        lesson_id: int,
    ) -> list[LessonLearningItemAssignment]:
        return self.assignment_repository.find_by_lesson_id(lesson_id)

    def replace_lesson_learning_items(
        self,
        lesson_id: int,
        assignments: list[LessonLearningItemAssignment],
    ) -> list[LessonLearningItemAssignment]:
        self.assignment_validator.validate_assignment_collection(assignments)

        return self.assignment_repository.replace_lesson_learning_items(
            lesson_id,
            assignments,
        )
