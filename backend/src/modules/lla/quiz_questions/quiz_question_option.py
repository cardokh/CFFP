"""
Quiz question option domain model.

Represents a selectable answer option for a quiz question
in the LLA application.
"""


class QuizQuestionOption:
    def __init__(
        self,
        option_id: int | None,
        question_id: int,
        option_text: str,
        is_correct: bool,
        display_order: int,
        created_at: str | None = None,
        updated_at: str | None = None,
        updated_by: str | None = None,
    ):
        self.option_id = option_id
        self.question_id = question_id
        self.option_text = option_text
        self.is_correct = is_correct
        self.display_order = display_order
        self.created_at = created_at
        self.updated_at = updated_at
        self.updated_by = updated_by

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
