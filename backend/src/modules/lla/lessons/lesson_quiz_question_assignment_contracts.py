"""
Lesson quiz question assignment contracts.

Responsibilities:
- Define request and response structures for lesson quiz question assignments.
- Centralize API-friendly response serialization.
"""

from dataclasses import dataclass, field

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.lessons.lesson_quiz_question_assignment import (
    LessonQuizQuestionAssignment,
)
from src.modules.lla.quiz_questions.quiz_question_option_contracts import (
    QuizQuestionOptionDetails,
)
from src.modules.lla.quiz_questions.quiz_question_option import (
    QuizQuestionOption,
)


@dataclass(frozen=True)
class LessonQuizQuestionAssignmentRequest:
    lesson_id: int
    question_id: int
    display_order: int


@dataclass(frozen=True)
class LessonQuizQuestionAssignmentDetails:
    lesson_id: int
    question_id: int
    display_order: int
    question_text: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    is_active: bool | None = None
    options: list[QuizQuestionOptionDetails] = field(default_factory=list)

    @classmethod
    def from_domain(
        cls,
        assignment: LessonQuizQuestionAssignment,
        options: list[QuizQuestionOption] | None = None,
    ):
        option_details = [
            QuizQuestionOptionDetails.from_domain(option) for option in (options or [])
        ]

        return cls(
            lesson_id=assignment.lesson_id,
            question_id=assignment.question_id,
            display_order=assignment.display_order,
            question_text=assignment.question_text,
            category_id=assignment.category_id,
            category_name=assignment.category_name,
            is_active=assignment.is_active,
            options=option_details,
        )

    def to_dict(self):
        return {
            "lesson_id": self.lesson_id,
            "question_id": self.question_id,
            "display_order": self.display_order,
            "question_text": self.question_text,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "is_active": self.is_active,
            "options": [option.to_dict() for option in self.options],
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())
