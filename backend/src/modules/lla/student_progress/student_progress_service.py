"""
Student progress application service.

Responsibilities:
- Coordinate student progress read use cases.
- Keep route handlers separate from repository/database details.
- Return student progress domain objects.

Architecture:
Routes -> Service -> Repository -> SQLite
"""


class StudentProgressService:
    def __init__(
        self,
        student_progress_repository,
    ):
        self.student_progress_repository = student_progress_repository

    def get_student_progress_overview(
        self,
        user_id: int,
    ):
        return self.student_progress_repository.get_student_progress_overview(
            user_id,
        )
