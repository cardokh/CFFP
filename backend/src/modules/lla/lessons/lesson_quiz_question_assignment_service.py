"""
Lesson quiz question assignment service.

Responsibilities:
- Coordinate ordered quiz question assignment use cases.
- Delegate validation to the assignment validator.
- Work with assignment domain objects only.
"""

from src.modules.lla.lessons.lesson_quiz_question_assignment import (
    LessonQuizQuestionAssignment,
)


class LessonQuizQuestionAssignmentService:
    def __init__(
        self,
        assignment_repository,
        assignment_validator,
        quiz_question_option_service,
    ):
        self.assignment_repository = assignment_repository
        self.assignment_validator = assignment_validator
        self.quiz_question_option_service = quiz_question_option_service

    def get_assignments_by_lesson_id(
        self,
        lesson_id: int,
    ) -> list[LessonQuizQuestionAssignment]:
        assignments = self.assignment_repository.find_by_lesson_id(lesson_id)

        for assignment in assignments:
            assignment.options = (
                self.quiz_question_option_service.get_options_by_question_id(
                    assignment.question_id
                )
            )

        return assignments

    def replace_lesson_quiz_questions(
        self,
        lesson_id: int,
        assignments: list[LessonQuizQuestionAssignment],
    ) -> list[LessonQuizQuestionAssignment]:
        self.assignment_validator.validate_assignment_collection(assignments)

        return self.assignment_repository.replace_lesson_quiz_questions(
            lesson_id,
            assignments,
        )
