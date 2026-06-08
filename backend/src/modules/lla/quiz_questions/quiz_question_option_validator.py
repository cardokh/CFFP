"""
Quiz question option validation.

Responsibilities:
- Validate quiz question option business rules.
- Keep validation concerns separate from service orchestration.
- Validate quiz question option domain objects only.
- Validate quiz question option collections for aggregate consistency.

Architecture:
Service -> Validator -> Repository
"""

from src.modules.lla.quiz_questions.quiz_question_option import QuizQuestionOption
from src.modules.lla.quiz_questions.quiz_question_option_messages import (
    EXACTLY_ONE_CORRECT_ANSWER_REQUIRED_MESSAGE,
    INVALID_ANSWER_OPTION_ORDER_MESSAGE,
    INVALID_DISPLAY_ORDER_MESSAGE,
    INVALID_QUIZ_QUESTION_ID_MESSAGE,
    INVALID_QUIZ_QUESTION_OPTION_ID_MESSAGE,
    MINIMUM_ANSWER_OPTIONS_REQUIRED_MESSAGE,
    OPTION_TEXT_REQUIRED_MESSAGE,
)


class QuizQuestionOptionValidator:
    MINIMUM_OPTION_COUNT = 2

    def validate_create_quiz_question_option(
        self,
        quiz_question_option: QuizQuestionOption,
    ):
        self._validate_quiz_question_option_fields(quiz_question_option)

    def validate_update_quiz_question_option(
        self,
        quiz_question_option: QuizQuestionOption,
    ):
        self.validate_quiz_question_option_id(quiz_question_option)
        self._validate_quiz_question_option_fields(quiz_question_option)

    @staticmethod
    def validate_quiz_question_option_id(
        quiz_question_option: QuizQuestionOption,
    ):
        if (
            quiz_question_option.option_id is None
            or quiz_question_option.option_id <= 0
        ):
            raise ValueError(INVALID_QUIZ_QUESTION_OPTION_ID_MESSAGE)

    @staticmethod
    def validate_quiz_question_id(
        quiz_question_option: QuizQuestionOption,
    ):
        if (
            quiz_question_option.question_id is None
            or quiz_question_option.question_id <= 0
        ):
            raise ValueError(INVALID_QUIZ_QUESTION_ID_MESSAGE)

    def validate_quiz_question_option_collection(
        self,
        quiz_question_options: list[QuizQuestionOption],
    ):
        if len(quiz_question_options) < self.MINIMUM_OPTION_COUNT:
            raise ValueError(MINIMUM_ANSWER_OPTIONS_REQUIRED_MESSAGE)

        correct_options = [
            quiz_question_option
            for quiz_question_option in quiz_question_options
            if quiz_question_option.is_correct
        ]

        if len(correct_options) != 1:
            raise ValueError(EXACTLY_ONE_CORRECT_ANSWER_REQUIRED_MESSAGE)

        for expected_display_order, quiz_question_option in enumerate(
            quiz_question_options,
            start=1,
        ):
            self._validate_quiz_question_option_fields(quiz_question_option)

            if quiz_question_option.display_order != expected_display_order:
                raise ValueError(INVALID_ANSWER_OPTION_ORDER_MESSAGE)

    @staticmethod
    def _validate_quiz_question_option_fields(
        quiz_question_option: QuizQuestionOption,
    ):
        if (
            quiz_question_option.question_id is None
            or quiz_question_option.question_id <= 0
        ):
            raise ValueError(INVALID_QUIZ_QUESTION_ID_MESSAGE)

        if not quiz_question_option.option_text:
            raise ValueError(OPTION_TEXT_REQUIRED_MESSAGE)

        if quiz_question_option.display_order <= 0:
            raise ValueError(INVALID_DISPLAY_ORDER_MESSAGE)
