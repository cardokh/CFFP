"""
User lesson assignment contracts.

Responsibilities:
- Define standardized request and response structures for user lesson assignments.
- Keep API response formats centralized and reusable.
- Preserve snake_case internally and convert to camelCase only at the response boundary.

Architecture:
routes -> mapper/contracts -> service -> repository
"""

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.user_lesson_assignments.user_lesson_assignment import (
    UserLessonAssignment,
)


class GetUserLessonAssignmentsRequest:
    """
    Request DTO for reading assigned lessons for one user.
    """

    def __init__(
        self,
        user_id: int,
    ):
        self.user_id = user_id


class ReplaceUserLessonAssignmentsRequest:
    """
    Request DTO for replacing all assigned lessons for one user.
    """

    def __init__(
        self,
        user_id: int,
        lesson_ids: list[int],
    ):
        self.user_id = user_id
        self.lesson_ids = lesson_ids


class UserLessonStatusUpdateRequest:
    """
    Request DTO for changing the status of one assigned lesson for one user.
    """

    def __init__(
        self,
        user_id: int,
        lesson_id: int,
        score: int | None = None,
        total_questions: int | None = None,
    ):
        self.user_id = user_id
        self.lesson_id = lesson_id
        self.score = score
        self.total_questions = total_questions


class SignupStudentLessonRequest:
    """
    Request DTO for signing one student up for one lesson.
    """

    def __init__(
        self,
        user_id: int,
        lesson_id: int,
    ):
        self.user_id = user_id
        self.lesson_id = lesson_id


class RemoveStudentLessonRequest:
    """
    Request DTO for removing one lesson from one student's library.
    """

    def __init__(
        self,
        user_id: int,
        lesson_id: int,
    ):
        self.user_id = user_id
        self.lesson_id = lesson_id


class UserLessonAssignmentDetails:
    """
    Detailed user lesson assignment response DTO.
    """

    @staticmethod
    def to_dict(
        assignment: UserLessonAssignment,
    ) -> dict:
        return {
            "user_id": assignment.user_id,
            "lesson_id": assignment.lesson_id,
            "is_active": assignment.is_active,
            "assigned_at": assignment.assigned_at,
            "started_at": assignment.started_at,
            "completed_at": assignment.completed_at,
            "updated_at": assignment.updated_at,
            "lesson_status_type_id": assignment.lesson_status_type_id,
            "lesson_status_code": assignment.lesson_status_code,
            "lesson_status_name": assignment.lesson_status_name,
            "lesson_title": assignment.lesson_title,
            "category_id": assignment.category_id,
            "category_name": assignment.category_name,
            "lesson_type_id": assignment.lesson_type_id,
            "lesson_type_name": assignment.lesson_type_name,
            "embodiment_type_id": assignment.embodiment_type_id,
            "embodiment_type_name": assignment.embodiment_type_name,
            "interaction_style_id": assignment.interaction_style_id,
            "interaction_style_name": assignment.interaction_style_name,
        }

    @staticmethod
    def to_camel_dict(assignment: UserLessonAssignment) -> dict:
        return dict_keys_to_camel_case(UserLessonAssignmentDetails.to_dict(assignment))
