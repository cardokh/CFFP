"""
Quiz question validation.

Responsibilities:
- Validate quiz question business rules.
- Keep validation concerns separate from service orchestration.
- Validate quiz question domain objects only.

Architecture:
Service -> Validator -> Repository
"""

from src.modules.lla.quiz_questions.quiz_question import QuizQuestion
from src.modules.lla.quiz_questions.quiz_question_messages import (
    DUPLICATE_QUIZ_QUESTION_MESSAGE,
    INVALID_CATEGORY_ID_MESSAGE,
    INVALID_QUIZ_QUESTION_ID_MESSAGE,
    QUESTION_TEXT_REQUIRED_MESSAGE,
)


class QuizQuestionValidator:
    def __init__(self, quiz_question_repository):
        self.quiz_question_repository = quiz_question_repository

    def validate_create_quiz_question(
        self,
        quiz_question: QuizQuestion,
    ):
        self._validate_quiz_question_fields(quiz_question)

        existing_question = self.quiz_question_repository.find_by_question_text(
            quiz_question
        )

        if existing_question is not None:
            raise ValueError(DUPLICATE_QUIZ_QUESTION_MESSAGE)

    def validate_update_quiz_question(
        self,
        quiz_question: QuizQuestion,
    ):
        self.validate_quiz_question_id(quiz_question)

        self._validate_quiz_question_fields(quiz_question)

        existing_question_with_text = (
            self.quiz_question_repository.find_by_question_text(quiz_question)
        )

        if (
            existing_question_with_text is not None
            and existing_question_with_text.question_id != quiz_question.question_id
        ):
            raise ValueError(DUPLICATE_QUIZ_QUESTION_MESSAGE)

    @staticmethod
    def validate_quiz_question_id(quiz_question: QuizQuestion):
        if quiz_question.question_id is None or quiz_question.question_id <= 0:
            raise ValueError(INVALID_QUIZ_QUESTION_ID_MESSAGE)

    @staticmethod
    def _validate_quiz_question_fields(
        quiz_question: QuizQuestion,
    ):
        if quiz_question.category_id is None or quiz_question.category_id <= 0:
            raise ValueError(INVALID_CATEGORY_ID_MESSAGE)

        if not quiz_question.question_text:
            raise ValueError(QUESTION_TEXT_REQUIRED_MESSAGE)
