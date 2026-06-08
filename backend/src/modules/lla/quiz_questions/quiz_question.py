"""
Quiz question domain model.

Represents a quiz question used in lessons in the LLA application.

The selectable answers are represented separately by QuizQuestionOption.
"""


class QuizQuestion:
    def __init__(
        self,
        question_id: int | None,
        category_id: int,
        question_text: str,
        is_active: bool,
        category_name: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        updated_by: str | None = None,
    ):
        self.question_id = question_id
        self.category_id = category_id
        self.category_name = category_name
        self.question_text = question_text
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.updated_by = updated_by

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
        }
