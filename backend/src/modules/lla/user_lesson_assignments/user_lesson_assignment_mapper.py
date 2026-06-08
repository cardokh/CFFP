"""
User lesson assignment mapper utilities.

Responsibilities:
- Convert database rows into UserLessonAssignment domain objects.
- Convert route parameters and payloads into request DTOs.
- Convert domain objects into API response dictionaries.
- Keep mapping logic centralized and reusable.

Architecture:
repository rows -> mapper -> domain model -> contracts
routes -> mapper -> request contracts -> service
"""

from src.modules.lla.user_lesson_assignments.user_lesson_assignment import (
    UserLessonAssignment,
)
from src.modules.lla.user_lesson_assignments.user_lesson_assignment_contracts import (
    GetUserLessonAssignmentsRequest,
    RemoveStudentLessonRequest,
    ReplaceUserLessonAssignmentsRequest,
    SignupStudentLessonRequest,
    UserLessonAssignmentDetails,
    UserLessonStatusUpdateRequest,
)


class UserLessonAssignmentMapper:
    @staticmethod
    def from_database_row(row) -> UserLessonAssignment:
        return UserLessonAssignment(
            user_id=row[0],
            lesson_id=row[1],
            is_active=bool(row[2]),
            assigned_at=row[3],
            started_at=row[4],
            completed_at=row[5],
            updated_at=row[6],
            lesson_status_type_id=row[7],
            lesson_status_code=row[8],
            lesson_status_name=row[9],
            lesson_title=row[10],
            category_id=row[11],
            category_name=row[12],
            lesson_type_id=row[13],
            lesson_type_name=row[14],
            embodiment_type_id=row[15],
            embodiment_type_name=row[16],
            interaction_style_id=row[17],
            interaction_style_name=row[18],
        )

    @staticmethod
    def get_request_from_user_id(
        user_id: int,
    ) -> GetUserLessonAssignmentsRequest:
        return GetUserLessonAssignmentsRequest(
            user_id=user_id,
        )

    @staticmethod
    def replace_request_from_payload(
        user_id: int,
        payload: dict,
    ) -> ReplaceUserLessonAssignmentsRequest:
        lesson_ids = [lesson["lesson_id"] for lesson in payload["lessons"]]

        return ReplaceUserLessonAssignmentsRequest(
            user_id=user_id,
            lesson_ids=lesson_ids,
        )

    @staticmethod
    def status_update_request_from_ids(
        user_id: int,
        lesson_id: int,
    ) -> UserLessonStatusUpdateRequest:
        return UserLessonStatusUpdateRequest(
            user_id=user_id,
            lesson_id=lesson_id,
        )

    @staticmethod
    def status_update_request_from_payload(
        user_id: int,
        payload: dict,
    ) -> UserLessonStatusUpdateRequest:
        return UserLessonStatusUpdateRequest(
            user_id=user_id,
            lesson_id=payload.get("lesson_id"),
            score=payload.get("score"),
            total_questions=payload.get("total_questions"),
        )

    @staticmethod
    def signup_student_lesson_request_from_ids(
        user_id: int,
        lesson_id: int,
    ) -> SignupStudentLessonRequest:
        return SignupStudentLessonRequest(
            user_id=user_id,
            lesson_id=lesson_id,
        )

    @staticmethod
    def remove_student_lesson_request_from_ids(
        user_id: int,
        lesson_id: int,
    ) -> RemoveStudentLessonRequest:
        return RemoveStudentLessonRequest(
            user_id=user_id,
            lesson_id=lesson_id,
        )

    @staticmethod
    def to_response_dict(
        assignment: UserLessonAssignment,
    ) -> dict:
        return UserLessonAssignmentDetails.to_camel_dict(assignment)

    @staticmethod
    def to_response_dict_list(
        assignments: list[UserLessonAssignment],
    ) -> list[dict]:
        return [
            UserLessonAssignmentMapper.to_response_dict(assignment)
            for assignment in assignments
        ]
