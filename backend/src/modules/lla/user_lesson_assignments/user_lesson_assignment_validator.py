"""
User lesson assignment validators.

Responsibilities:
- Validate incoming assignment payloads.
- Keep validation logic centralized and reusable.
- Prevent invalid lesson assignment structures from reaching services/repositories.

Architecture:
routes -> validator -> mapper -> service
"""

from src.modules.lla.user_lesson_assignments.user_lesson_assignment_messages import (
    INVALID_REQUEST_BODY,
    LESSONS_FIELD_IS_REQUIRED,
    LESSONS_MUST_BE_A_LIST,
)


class UserLessonAssignmentValidator:
    @staticmethod
    def validate_assignment_payload(payload: dict) -> None:
        if not isinstance(payload, dict):
            raise ValueError(INVALID_REQUEST_BODY)

        if "lessons" not in payload:
            raise ValueError(LESSONS_FIELD_IS_REQUIRED)

        lessons = payload["lessons"]

        if not isinstance(lessons, list):
            raise ValueError(LESSONS_MUST_BE_A_LIST)

        for lesson in lessons:
            UserLessonAssignmentValidator.validate_lesson_assignment(lesson)

    @staticmethod
    def validate_lesson_assignment(
        lesson_assignment: dict,
    ) -> None:
        if not isinstance(lesson_assignment, dict):
            raise ValueError(INVALID_REQUEST_BODY)

        UserLessonAssignmentValidator.validate_lesson_id_field(lesson_assignment)

    @staticmethod
    def validate_status_update_payload(payload: dict) -> None:
        if not isinstance(payload, dict):
            raise ValueError(INVALID_REQUEST_BODY)

        UserLessonAssignmentValidator.validate_lesson_id_field(payload)

    @staticmethod
    def validate_student_lesson_signup_payload(payload: dict) -> None:
        if not isinstance(payload, dict):
            raise ValueError(INVALID_REQUEST_BODY)

        UserLessonAssignmentValidator.validate_lesson_id_field(payload)

    @staticmethod
    def validate_student_lesson_remove_payload(payload: dict) -> None:
        if not isinstance(payload, dict):
            raise ValueError(INVALID_REQUEST_BODY)

        UserLessonAssignmentValidator.validate_lesson_id_field(payload)

    @staticmethod
    def validate_lesson_id_field(payload: dict) -> None:
        lesson_id = payload.get("lesson_id")

        if lesson_id is None:
            raise ValueError("lesson_id is required.")

        if not isinstance(lesson_id, int):
            raise ValueError("lesson_id must be an integer.")
