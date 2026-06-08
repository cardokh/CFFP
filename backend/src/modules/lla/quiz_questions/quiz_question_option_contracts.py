"""
Quiz question option contracts.

Responsibilities:
- Define request and response structures for quiz question option use cases.
- Keep API/service boundaries explicit and reusable.
- Centralize input normalization for create/update operations.
- Centralize API-friendly response serialization.

Architecture:
API -> Contracts -> QuizQuestionOptionService
-> QuizQuestionOptionRepository -> SQLite Database

Notes:
- These contracts are not domain objects.
- Domain objects represent internal business entities.
- Contracts represent boundary data moving into or out of use cases.
"""

from dataclasses import dataclass

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.quiz_questions.quiz_question_option import (
    QuizQuestionOption,
)

SYSTEM_UPDATED_BY = "system"


@dataclass(frozen=True)
class CreateQuizQuestionOptionRequest:
    question_id: int
    option_text: str
    is_correct: bool
    display_order: int
    updated_by: str | None = None

    @property
    def cleaned_option_text(self) -> str:
        return self.option_text.strip() if self.option_text else ""

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class UpdateQuizQuestionOptionRequest:
    option_id: int
    question_id: int
    option_text: str
    is_correct: bool
    display_order: int
    updated_by: str | None = None

    @property
    def cleaned_option_text(self) -> str:
        return self.option_text.strip() if self.option_text else ""

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
    def from_domain(
        cls,
        quiz_question_option: QuizQuestionOption,
    ):
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
