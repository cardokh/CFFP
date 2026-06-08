"""
Quiz question application service.

Responsibilities:
- Coordinate quiz question CRUD use cases.
- Keep API handlers separate from repository/database details.
- Delegate quiz question validation to the quiz question validator.
- Work with quiz question domain objects only.

Architecture:
API -> Mapper -> QuizQuestionService -> QuizQuestionValidator -> QuizQuestionRepository -> SQLite Database

Note:
Quiz question options are coordinated by QuizQuestionOptionService.
"""

from src.modules.lla.quiz_questions.quiz_question import QuizQuestion


class QuizQuestionService:
    def __init__(
        self,
        quiz_question_repository,
        quiz_question_validator,
    ):
        self.quiz_question_repository = quiz_question_repository
        self.quiz_question_validator = quiz_question_validator

    def get_all_quiz_questions(self) -> list[QuizQuestion]:
        return self.quiz_question_repository.find_all_quiz_questions()

    def get_quiz_question_by_id(
        self,
        quiz_question: QuizQuestion,
    ) -> QuizQuestion | None:
        self.quiz_question_validator.validate_quiz_question_id(quiz_question)

        return self.quiz_question_repository.find_by_id(quiz_question)

    def create_quiz_question(
        self,
        quiz_question: QuizQuestion,
    ) -> QuizQuestion:
        self.quiz_question_validator.validate_create_quiz_question(quiz_question)

        return self.quiz_question_repository.create_quiz_question(quiz_question)

    def update_quiz_question(
        self,
        quiz_question: QuizQuestion,
    ) -> QuizQuestion | None:
        self.quiz_question_validator.validate_update_quiz_question(quiz_question)

        return self.quiz_question_repository.update_quiz_question(quiz_question)

    def delete_quiz_question(
        self,
        quiz_question: QuizQuestion,
    ) -> bool:
        self.quiz_question_validator.validate_quiz_question_id(quiz_question)

        return self.quiz_question_repository.delete_quiz_question(quiz_question)
