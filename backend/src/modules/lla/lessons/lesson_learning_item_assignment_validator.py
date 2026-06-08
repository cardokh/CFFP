"""
Lesson learning item assignment validator.

Responsibilities:
- Validate lesson learning item assignment business rules.
- Validate assignment collections for aggregate replacement.
"""

from src.modules.lla.lessons.lesson_learning_item_assignment import (
    LessonLearningItemAssignment,
)
from src.modules.lla.lessons.lesson_learning_item_assignment_messages import (
    INVALID_ASSIGNMENT_ORDER_MESSAGE,
    INVALID_DISPLAY_ORDER_MESSAGE,
    INVALID_LEARNING_ITEM_ID_MESSAGE,
    INVALID_LESSON_ID_MESSAGE,
)


class LessonLearningItemAssignmentValidator:
    def validate_assignment_collection(
        self,
        assignments: list[LessonLearningItemAssignment],
    ):
        for expected_display_order, assignment in enumerate(assignments, start=1):
            self._validate_assignment_fields(assignment)

            if assignment.display_order != expected_display_order:
                raise ValueError(INVALID_ASSIGNMENT_ORDER_MESSAGE)

    @staticmethod
    def _validate_assignment_fields(
        assignment: LessonLearningItemAssignment,
    ):
        if assignment.lesson_id is None or assignment.lesson_id <= 0:
            raise ValueError(INVALID_LESSON_ID_MESSAGE)

        if assignment.item_id is None or assignment.item_id <= 0:
            raise ValueError(INVALID_LEARNING_ITEM_ID_MESSAGE)

        if assignment.display_order <= 0:
            raise ValueError(INVALID_DISPLAY_ORDER_MESSAGE)
