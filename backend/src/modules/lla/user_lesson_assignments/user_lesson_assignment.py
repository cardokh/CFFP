"""
User lesson assignment domain model.

Represents the relationship between a platform user and an assigned LLA lesson.

Users themselves belong to the reusable core/platform layer.
The assignment of lessons to users belongs to the LLA module.
"""


class UserLessonAssignment:
    def __init__(
        self,
        user_id: int,
        lesson_id: int,
        is_active: bool,
        assigned_at: str | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
        updated_at: str | None = None,
        lesson_status_type_id: int | None = None,
        lesson_status_code: str | None = None,
        lesson_status_name: str | None = None,
        lesson_title: str | None = None,
        category_id: int | None = None,
        category_name: str | None = None,
        lesson_type_id: int | None = None,
        lesson_type_name: str | None = None,
        embodiment_type_id: int | None = None,
        embodiment_type_name: str | None = None,
        interaction_style_id: int | None = None,
        interaction_style_name: str | None = None,
    ):
        self.user_id = user_id
        self.lesson_id = lesson_id
        self.is_active = is_active
        self.assigned_at = assigned_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.updated_at = updated_at
        self.lesson_status_type_id = lesson_status_type_id
        self.lesson_status_code = lesson_status_code
        self.lesson_status_name = lesson_status_name
        self.lesson_title = lesson_title
        self.category_id = category_id
        self.category_name = category_name
        self.lesson_type_id = lesson_type_id
        self.lesson_type_name = lesson_type_name
        self.embodiment_type_id = embodiment_type_id
        self.embodiment_type_name = embodiment_type_name
        self.interaction_style_id = interaction_style_id
        self.interaction_style_name = interaction_style_name

    def to_dict(self):
        return {
            "userId": self.user_id,
            "lessonId": self.lesson_id,
            "isActive": self.is_active,
            "assignedAt": self.assigned_at,
            "startedAt": self.started_at,
            "completedAt": self.completed_at,
            "updatedAt": self.updated_at,
            "lessonStatusTypeId": self.lesson_status_type_id,
            "lessonStatusCode": self.lesson_status_code,
            "lessonStatusName": self.lesson_status_name,
            "lessonTitle": self.lesson_title,
            "categoryId": self.category_id,
            "categoryName": self.category_name,
            "lessonTypeId": self.lesson_type_id,
            "lessonTypeName": self.lesson_type_name,
            "embodimentTypeId": self.embodiment_type_id,
            "embodimentTypeName": self.embodiment_type_name,
            "interactionStyleId": self.interaction_style_id,
            "interactionStyleName": self.interaction_style_name,
        }
