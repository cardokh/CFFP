"""
Lesson quiz question assignment domain model.

Represents an ordered assignment between a lesson and a quiz question.
"""

from src.modules.lla.quiz_questions.quiz_question_option import (
    QuizQuestionOption,
)


class LessonQuizQuestionAssignment:
    def __init__(
        self,
        lesson_id: int,
        question_id: int,
        display_order: int,
        question_text: str | None = None,
        category_id: int | None = None,
        category_name: str | None = None,
        is_active: bool | None = None,
        options: list[QuizQuestionOption] | None = None,
    ):
        self.lesson_id = lesson_id
        self.question_id = question_id
        self.display_order = display_order
        self.question_text = question_text
        self.category_id = category_id
        self.category_name = category_name
        self.is_active = is_active
        self.options = options or []
