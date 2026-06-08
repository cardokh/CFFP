"""
Student progress domain models.

Represents the progress overview shown to a student.

Architecture:
Repository -> Domain -> Service -> Contracts -> Routes -> JSON
"""


class StudentProgressSummary:
    def __init__(
        self,
        total_lessons: int,
        completed_lessons: int,
        in_progress_lessons: int,
        not_started_lessons: int,
        completion_percentage: float,
    ):
        self.total_lessons = total_lessons
        self.completed_lessons = completed_lessons
        self.in_progress_lessons = in_progress_lessons
        self.not_started_lessons = not_started_lessons
        self.completion_percentage = completion_percentage


class StudentProgressLesson:
    def __init__(
        self,
        lesson_id: int,
        lesson_title: str,
        category_name: str | None,
        lesson_type_name: str | None,
        lesson_status_code: str | None,
        lesson_status_name: str | None,
        assigned_at: str | None,
        started_at: str | None,
        completed_at: str | None,
        score: int | None = None,
        total_questions: int | None = None,
    ):
        self.lesson_id = lesson_id
        self.lesson_title = lesson_title
        self.category_name = category_name
        self.lesson_type_name = lesson_type_name
        self.lesson_status_code = lesson_status_code
        self.lesson_status_name = lesson_status_name
        self.assigned_at = assigned_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.score = score
        self.total_questions = total_questions


class StudentProgressOverview:
    def __init__(
        self,
        summary: StudentProgressSummary,
        completed_lessons: list[StudentProgressLesson],
        continue_lessons: list[StudentProgressLesson],
    ):
        self.summary = summary
        self.completed_lessons = completed_lessons
        self.continue_lessons = continue_lessons
