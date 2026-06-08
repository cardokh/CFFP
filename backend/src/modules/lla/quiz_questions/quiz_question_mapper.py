"""
Quiz question mapper.

Responsibilities:
- Convert quiz question request contracts into domain objects.
- Convert quiz question domain objects into response contracts.
- Convert quiz question option domain objects into response contracts.
- Centralize mapping logic between architectural layers.

Architecture:
Contracts <-> Mapper <-> Domain
"""

from src.modules.lla.quiz_questions.quiz_question import QuizQuestion
from src.modules.lla.quiz_questions.quiz_question_option import QuizQuestionOption
from src.modules.lla.quiz_questions.quiz_question_contracts import (
    CreateQuizQuestionRequest,
    QuizQuestionDetails,
    UpdateQuizQuestionRequest,
)


class QuizQuestionMapper:
    @staticmethod
    def create_request_to_domain(
        request: CreateQuizQuestionRequest,
    ) -> QuizQuestion:
        return QuizQuestion(
            question_id=None,
            category_id=request.category_id,
            question_text=request.cleaned_question_text,
            is_active=request.is_active,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def update_request_to_domain(
        request: UpdateQuizQuestionRequest,
    ) -> QuizQuestion:
        return QuizQuestion(
            question_id=request.question_id,
            category_id=request.category_id,
            question_text=request.cleaned_question_text,
            is_active=request.is_active,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def question_id_to_domain(question_id: int) -> QuizQuestion:
        return QuizQuestion(
            question_id=question_id,
            category_id=0,
            question_text="",
            is_active=True,
        )

    @staticmethod
    def question_text_to_domain(question_text: str) -> QuizQuestion:
        return QuizQuestion(
            question_id=None,
            category_id=0,
            question_text=question_text,
            is_active=True,
        )

    @staticmethod
    def domain_to_details(
        quiz_question: QuizQuestion,
        options: list[QuizQuestionOption] | None = None,
    ) -> QuizQuestionDetails:
        return QuizQuestionDetails.from_domain(
            quiz_question,
            options,
        )
