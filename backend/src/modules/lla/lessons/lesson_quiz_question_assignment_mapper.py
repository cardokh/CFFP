"""
Lesson quiz question assignment mapper.

Responsibilities:
- Convert request contracts into domain objects.
- Convert domain objects into response contracts.
"""

from src.modules.lla.lessons.lesson_quiz_question_assignment import (
    LessonQuizQuestionAssignment,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_contracts import (
    LessonQuizQuestionAssignmentDetails,
    LessonQuizQuestionAssignmentRequest,
)


class LessonQuizQuestionAssignmentMapper:
    @staticmethod
    def request_to_domain(
        request: LessonQuizQuestionAssignmentRequest,
    ) -> LessonQuizQuestionAssignment:
        return LessonQuizQuestionAssignment(
            lesson_id=request.lesson_id,
            question_id=request.question_id,
            display_order=request.display_order,
        )

    @staticmethod
    def domain_to_details(
        assignment: LessonQuizQuestionAssignment,
    ) -> LessonQuizQuestionAssignmentDetails:
        return LessonQuizQuestionAssignmentDetails.from_domain(
            assignment,
            assignment.options,
        )
