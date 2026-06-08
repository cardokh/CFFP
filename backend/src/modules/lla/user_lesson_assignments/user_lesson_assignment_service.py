"""
User lesson assignment service.

Responsibilities:
- Coordinate user lesson assignment use cases.
- Keep route handlers separate from repository/database details.
- Receive typed request DTOs from the route/mapper boundary.
- Return assignment domain objects.

Architecture:
routes -> mapper/contracts -> service -> repository -> SQLite
"""

from src.modules.lla.user_lesson_assignments.user_lesson_assignment_contracts import (
    GetUserLessonAssignmentsRequest,
    RemoveStudentLessonRequest,
    ReplaceUserLessonAssignmentsRequest,
    SignupStudentLessonRequest,
    UserLessonStatusUpdateRequest,
)


class UserLessonAssignmentService:
    def __init__(
        self,
        user_lesson_assignment_repository,
        user_lesson_assignment_validator,
    ):
        self.user_lesson_assignment_repository = user_lesson_assignment_repository
        self.user_lesson_assignment_validator = user_lesson_assignment_validator

    def get_user_lesson_assignments(
        self,
        request: GetUserLessonAssignmentsRequest,
    ) -> list:
        return self.user_lesson_assignment_repository.get_user_lesson_assignments(
            request
        )

    def replace_user_lesson_assignments(
        self,
        request: ReplaceUserLessonAssignmentsRequest,
    ) -> list:
        self.user_lesson_assignment_repository.replace_user_lesson_assignments(request)

        return self.user_lesson_assignment_repository.get_user_lesson_assignments(
            request
        )

    def mark_lesson_in_progress(
        self,
        request: UserLessonStatusUpdateRequest,
    ) -> list:
        self.user_lesson_assignment_repository.mark_lesson_in_progress(request)

        return self.user_lesson_assignment_repository.get_user_lesson_assignments(
            request
        )

    def mark_lesson_completed(
        self,
        request: UserLessonStatusUpdateRequest,
    ) -> list:
        self.user_lesson_assignment_repository.mark_lesson_completed(request)

        return self.user_lesson_assignment_repository.get_user_lesson_assignments(
            request
        )

    def get_student_lessons(
        self,
        request: GetUserLessonAssignmentsRequest,
    ) -> list:
        return self.user_lesson_assignment_repository.get_student_lessons(request)

    def signup_student_lesson(
        self,
        request: SignupStudentLessonRequest,
    ) -> list:
        self.user_lesson_assignment_repository.signup_student_lesson(request)

        return self.user_lesson_assignment_repository.get_student_lessons(request)

    def remove_student_lesson(
        self,
        request: RemoveStudentLessonRequest,
    ) -> list:
        self.user_lesson_assignment_repository.remove_student_lesson(request)

        return self.user_lesson_assignment_repository.get_student_lessons(request)
