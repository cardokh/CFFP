"""
Quiz question option application service.

Responsibilities:
- Coordinate quiz question option CRUD use cases.
- Keep API handlers separate from repository/database details.
- Delegate quiz question option validation to the validator.
- Work with quiz question option domain objects only.
- Support aggregate-style replacement of options for a quiz question.

Architecture:
API -> Mapper -> QuizQuestionOptionService -> QuizQuestionOptionValidator
-> QuizQuestionOptionRepository -> SQLite Database
"""

from src.modules.lla.quiz_questions.quiz_question_option import (
    QuizQuestionOption,
)


class QuizQuestionOptionService:
    def __init__(
        self,
        quiz_question_option_repository,
        quiz_question_option_validator,
    ):
        self.quiz_question_option_repository = quiz_question_option_repository
        self.quiz_question_option_validator = quiz_question_option_validator

    def get_options_by_question_id(
        self,
        question_id: int,
    ) -> list[QuizQuestionOption]:
        return self.quiz_question_option_repository.find_by_question_id(question_id)

    def get_quiz_question_option_by_id(
        self,
        quiz_question_option: QuizQuestionOption,
    ) -> QuizQuestionOption | None:
        self.quiz_question_option_validator.validate_quiz_question_option_id(
            quiz_question_option
        )

        return self.quiz_question_option_repository.find_by_id(quiz_question_option)

    def create_quiz_question_option(
        self,
        quiz_question_option: QuizQuestionOption,
    ) -> QuizQuestionOption:
        self.quiz_question_option_validator.validate_create_quiz_question_option(
            quiz_question_option
        )

        return self.quiz_question_option_repository.create_quiz_question_option(
            quiz_question_option
        )

    def update_quiz_question_option(
        self,
        quiz_question_option: QuizQuestionOption,
    ) -> QuizQuestionOption | None:
        self.quiz_question_option_validator.validate_update_quiz_question_option(
            quiz_question_option
        )

        return self.quiz_question_option_repository.update_quiz_question_option(
            quiz_question_option
        )

    def delete_quiz_question_option(
        self,
        quiz_question_option: QuizQuestionOption,
    ) -> bool:
        self.quiz_question_option_validator.validate_quiz_question_option_id(
            quiz_question_option
        )

        return self.quiz_question_option_repository.delete_quiz_question_option(
            quiz_question_option
        )

    def replace_question_options(
        self,
        question_id: int,
        quiz_question_options: list[QuizQuestionOption],
    ) -> list[QuizQuestionOption]:
        self.quiz_question_option_validator.validate_quiz_question_option_collection(
            quiz_question_options
        )

        return self.quiz_question_option_repository.replace_question_options(
            question_id,
            quiz_question_options,
        )
