"""
Quiz question contracts.

Responsibilities:
- Define request and response structures for quiz question use cases.
- Keep API/service boundaries explicit and reusable.
- Centralize input normalization for quiz question create/update operations.
- Centralize API-friendly response serialization.
- Include selectable answer options in quiz question detail responses.

Architecture:
API -> Contracts -> QuizQuestionService -> QuizQuestionRepository -> SQLite Database

Notes:
- These contracts are not domain objects.
- Domain objects represent internal business entities.
- Contracts represent boundary data moving into or out of use cases.
- Correct answers are represented by QuizQuestionOption.is_correct, not by QuizQuestion.
"""

from dataclasses import dataclass, field

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.quiz_questions.quiz_question import QuizQuestion
from src.modules.lla.quiz_questions.quiz_question_option import QuizQuestionOption

SYSTEM_UPDATED_BY = "system"


@dataclass(frozen=True)
class CreateQuizQuestionRequest:
    category_id: int
    question_text: str
    is_active: bool
    updated_by: str | None = None

    @property
    def cleaned_question_text(self) -> str:
        return self.question_text.strip() if self.question_text else ""

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class UpdateQuizQuestionRequest:
    question_id: int
    category_id: int
    question_text: str
    is_active: bool
    updated_by: str | None = None

    @property
    def cleaned_question_text(self) -> str:
        return self.question_text.strip() if self.question_text else ""

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class QuizQuestionOptionDetails:
    option_id: int | None
    question_id: int
    option_text: str
    is_correct: bool
    display_order: int
    created_at: str | None
    updated_at: str | None
    updated_by: str | None

    @classmethod
    def from_domain(cls, quiz_question_option: QuizQuestionOption):
        return cls(
            option_id=quiz_question_option.option_id,
            question_id=quiz_question_option.question_id,
            option_text=quiz_question_option.option_text,
            is_correct=quiz_question_option.is_correct,
            display_order=quiz_question_option.display_order,
            created_at=quiz_question_option.created_at,
            updated_at=quiz_question_option.updated_at,
            updated_by=quiz_question_option.updated_by,
        )

    def to_dict(self):
        return {
            "optionId": self.option_id,
            "questionId": self.question_id,
            "optionText": self.option_text,
            "isCorrect": self.is_correct,
            "displayOrder": self.display_order,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "updatedBy": self.updated_by,
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())


@dataclass(frozen=True)
class QuizQuestionDetails:
    question_id: int | None
    category_id: int
    category_name: str | None
    question_text: str
    is_active: bool
    created_at: str | None
    updated_at: str | None
    updated_by: str | None
    options: list[QuizQuestionOptionDetails] = field(default_factory=list)

    @classmethod
    def from_domain(
        cls,
        quiz_question: QuizQuestion,
        options: list[QuizQuestionOption] | None = None,
    ):
        option_details = [
            QuizQuestionOptionDetails.from_domain(option) for option in (options or [])
        ]

        return cls(
            question_id=quiz_question.question_id,
            category_id=quiz_question.category_id,
            category_name=quiz_question.category_name,
            question_text=quiz_question.question_text,
            is_active=quiz_question.is_active,
            created_at=quiz_question.created_at,
            updated_at=quiz_question.updated_at,
            updated_by=quiz_question.updated_by,
            options=option_details,
        )

    def to_dict(self):
        return {
            "questionId": self.question_id,
            "categoryId": self.category_id,
            "categoryName": self.category_name,
            "questionText": self.question_text,
            "isActive": self.is_active,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "updatedBy": self.updated_by,
            "options": [option.to_dict() for option in self.options],
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())


QuizQuestionSummary = QuizQuestionDetails
