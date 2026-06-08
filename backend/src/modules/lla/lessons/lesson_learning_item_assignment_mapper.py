"""
Lesson learning item assignment mapper.

Responsibilities:
- Convert request contracts into domain objects.
- Convert domain objects into response contracts.
"""

from src.modules.lla.lessons.lesson_learning_item_assignment import (
    LessonLearningItemAssignment,
)
from src.modules.lla.lessons.lesson_learning_item_assignment_contracts import (
    LessonLearningItemAssignmentDetails,
    LessonLearningItemAssignmentRequest,
)


class LessonLearningItemAssignmentMapper:
    @staticmethod
    def request_to_domain(
        request: LessonLearningItemAssignmentRequest,
    ) -> LessonLearningItemAssignment:
        return LessonLearningItemAssignment(
            lesson_id=request.lesson_id,
            item_id=request.item_id,
            display_order=request.display_order,
        )

    @staticmethod
    def domain_to_details(
        assignment: LessonLearningItemAssignment,
    ) -> LessonLearningItemAssignmentDetails:
        return LessonLearningItemAssignmentDetails.from_domain(assignment)
