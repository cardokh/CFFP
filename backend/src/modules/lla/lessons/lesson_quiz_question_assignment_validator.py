"""
Lesson quiz question assignment validator.

Responsibilities:
- Validate lesson quiz question assignment business rules.
- Validate assignment collections for aggregate replacement.
"""

from src.modules.lla.lessons.lesson_quiz_question_assignment import (
    LessonQuizQuestionAssignment,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_messages import (
    INVALID_ASSIGNMENT_ORDER_MESSAGE,
    INVALID_DISPLAY_ORDER_MESSAGE,
    INVALID_LESSON_ID_MESSAGE,
    INVALID_QUIZ_QUESTION_ID_MESSAGE,
)


class LessonQuizQuestionAssignmentValidator:
    def validate_assignment_collection(
        self,
        assignments: list[LessonQuizQuestionAssignment],
    ):
        for expected_display_order, assignment in enumerate(assignments, start=1):
            self._validate_assignment_fields(assignment)

            if assignment.display_order != expected_display_order:
                raise ValueError(INVALID_ASSIGNMENT_ORDER_MESSAGE)

    @staticmethod
    def _validate_assignment_fields(
        assignment: LessonQuizQuestionAssignment,
    ):
        if assignment.lesson_id is None or assignment.lesson_id <= 0:
            raise ValueError(INVALID_LESSON_ID_MESSAGE)

        if assignment.question_id is None or assignment.question_id <= 0:
            raise ValueError(INVALID_QUIZ_QUESTION_ID_MESSAGE)

        if assignment.display_order <= 0:
            raise ValueError(INVALID_DISPLAY_ORDER_MESSAGE)
