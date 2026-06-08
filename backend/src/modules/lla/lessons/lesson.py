"""
Lesson domain model.

Represents a lesson in the LLA application.

A lesson connects category, lesson type, embodiment type,
and interaction style. Ordered learning items and ordered quiz questions
are represented separately through lesson composition tables.
"""


class Lesson:
    def __init__(
        self,
        lesson_id: int | None,
        category_id: int,
        lesson_type_id: int,
        embodiment_type_id: int,
        interaction_style_id: int,
        title: str,
        description: str | None,
        is_active: bool,
        category_name: str | None = None,
        lesson_type_name: str | None = None,
        embodiment_type_name: str | None = None,
        interaction_style_name: str | None = None,
        learning_items_count: int = 0,
        quiz_questions_count: int = 0,
        created_at: str | None = None,
        updated_at: str | None = None,
        updated_by: str | None = None,
    ):
        self.lesson_id = lesson_id
        self.category_id = category_id
        self.lesson_type_id = lesson_type_id
        self.embodiment_type_id = embodiment_type_id
        self.interaction_style_id = interaction_style_id
        self.title = title
        self.description = description
        self.is_active = is_active
        self.category_name = category_name
        self.lesson_type_name = lesson_type_name
        self.embodiment_type_name = embodiment_type_name
        self.interaction_style_name = interaction_style_name
        self.learning_items_count = learning_items_count
        self.quiz_questions_count = quiz_questions_count
        self.created_at = created_at
        self.updated_at = updated_at
        self.updated_by = updated_by

    def to_dict(self):
        return {
            "lessonId": self.lesson_id,
            "categoryId": self.category_id,
            "lessonTypeId": self.lesson_type_id,
            "embodimentTypeId": self.embodiment_type_id,
            "interactionStyleId": self.interaction_style_id,
            "title": self.title,
            "description": self.description,
            "isActive": self.is_active,
            "categoryName": self.category_name,
            "lessonTypeName": self.lesson_type_name,
            "embodimentTypeName": self.embodiment_type_name,
            "interactionStyleName": self.interaction_style_name,
            "learningItemsCount": self.learning_items_count,
            "quizQuestionsCount": self.quiz_questions_count,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "updatedBy": self.updated_by,
        }
