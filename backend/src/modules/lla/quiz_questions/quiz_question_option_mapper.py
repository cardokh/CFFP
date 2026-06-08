"""
Quiz question option mapper.

Responsibilities:
- Convert quiz question option request contracts into domain objects.
- Convert quiz question option domain objects into response contracts.
- Centralize mapping logic between architectural layers.

Architecture:
Contracts <-> Mapper <-> Domain
"""

from src.modules.lla.quiz_questions.quiz_question_option import (
    QuizQuestionOption,
)
from src.modules.lla.quiz_questions.quiz_question_option_contracts import (
    CreateQuizQuestionOptionRequest,
    QuizQuestionOptionDetails,
    UpdateQuizQuestionOptionRequest,
)


class QuizQuestionOptionMapper:
    @staticmethod
    def create_request_to_domain(
        request: CreateQuizQuestionOptionRequest,
    ) -> QuizQuestionOption:
        return QuizQuestionOption(
            option_id=None,
            question_id=request.question_id,
            option_text=request.cleaned_option_text,
            is_correct=request.is_correct,
            display_order=request.display_order,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def update_request_to_domain(
        request: UpdateQuizQuestionOptionRequest,
    ) -> QuizQuestionOption:
        return QuizQuestionOption(
            option_id=request.option_id,
            question_id=request.question_id,
            option_text=request.cleaned_option_text,
            is_correct=request.is_correct,
            display_order=request.display_order,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def option_id_to_domain(
        option_id: int,
    ) -> QuizQuestionOption:
        return QuizQuestionOption(
            option_id=option_id,
            question_id=0,
            option_text="",
            is_correct=False,
            display_order=1,
        )

    @staticmethod
    def domain_to_details(
        quiz_question_option: QuizQuestionOption,
    ) -> QuizQuestionOptionDetails:
        return QuizQuestionOptionDetails.from_domain(quiz_question_option)
