"""
Lesson category domain model.

Represents a category used to group lessons in the LLA application.
"""


class LessonCategory:
    def __init__(
        self,
        category_id: int | None,
        name: str,
        description: str | None,
        is_active: bool,
        created_at: str | None = None,
        updated_at: str | None = None,
        updated_by: str | None = None,
    ):
        self.category_id = category_id
        self.name = name
        self.description = description
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.updated_by = updated_by

    def to_dict(self):
        return {
            "categoryId": self.category_id,
            "name": self.name,
            "description": self.description,
            "isActive": self.is_active,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "updatedBy": self.updated_by,
        }
