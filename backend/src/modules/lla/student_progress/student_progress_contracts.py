"""
Student progress contracts.

Responsibilities:
- Define API response structures for student progress.
- Keep API response formatting separate from domain models.
- Convert snake_case internal fields to camelCase at the response boundary.

Architecture:
Domain -> Contracts -> Routes -> JSON
"""

from dataclasses import dataclass

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.student_progress.student_progress import (
    StudentProgressLesson,
    StudentProgressOverview,
    StudentProgressSummary,
)


@dataclass(frozen=True)
class StudentProgressSummaryDetails:
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    not_started_lessons: int
    completion_percentage: float

    @classmethod
    def from_domain(cls, summary: StudentProgressSummary):
        return cls(
            total_lessons=summary.total_lessons,
            completed_lessons=summary.completed_lessons,
            in_progress_lessons=summary.in_progress_lessons,
            not_started_lessons=summary.not_started_lessons,
            completion_percentage=summary.completion_percentage,
        )

    def to_dict(self):
        return {
            "total_lessons": self.total_lessons,
            "completed_lessons": self.completed_lessons,
            "in_progress_lessons": self.in_progress_lessons,
            "not_started_lessons": self.not_started_lessons,
            "completion_percentage": self.completion_percentage,
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())


@dataclass(frozen=True)
class StudentProgressLessonDetails:
    lesson_id: int
    lesson_title: str
    category_name: str | None
    lesson_type_name: str | None
    lesson_status_code: str | None
    lesson_status_name: str | None
    assigned_at: str | None
    started_at: str | None
    completed_at: str | None
    score: int | None
    total_questions: int | None

    @classmethod
    def from_domain(cls, lesson: StudentProgressLesson):
        return cls(
            lesson_id=lesson.lesson_id,
            lesson_title=lesson.lesson_title,
            category_name=lesson.category_name,
            lesson_type_name=lesson.lesson_type_name,
            lesson_status_code=lesson.lesson_status_code,
            lesson_status_name=lesson.lesson_status_name,
            assigned_at=lesson.assigned_at,
            started_at=lesson.started_at,
            completed_at=lesson.completed_at,
            score=lesson.score,
            total_questions=lesson.total_questions,
        )

    def to_dict(self):
        return {
            "lesson_id": self.lesson_id,
            "lesson_title": self.lesson_title,
            "category_name": self.category_name,
            "lesson_type_name": self.lesson_type_name,
            "lesson_status_code": self.lesson_status_code,
            "lesson_status_name": self.lesson_status_name,
            "assigned_at": self.assigned_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "score": self.score,
            "total_questions": self.total_questions,
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())


@dataclass(frozen=True)
class StudentProgressOverviewDetails:
    summary: StudentProgressSummaryDetails
    completed_lessons: list[StudentProgressLessonDetails]
    continue_lessons: list[StudentProgressLessonDetails]

    @classmethod
    def from_domain(cls, overview: StudentProgressOverview):
        return cls(
            summary=StudentProgressSummaryDetails.from_domain(overview.summary),
            completed_lessons=[
                StudentProgressLessonDetails.from_domain(lesson)
                for lesson in overview.completed_lessons
            ],
            continue_lessons=[
                StudentProgressLessonDetails.from_domain(lesson)
                for lesson in overview.continue_lessons
            ],
        )

    def to_dict(self):
        return {
            "summary": self.summary.to_dict(),
            "completed_lessons": [
                lesson.to_dict() for lesson in self.completed_lessons
            ],
            "continue_lessons": [lesson.to_dict() for lesson in self.continue_lessons],
        }

    def to_camel_dict(self):
        return {
            "summary": self.summary.to_camel_dict(),
            "completedLessons": [
                lesson.to_camel_dict() for lesson in self.completed_lessons
            ],
            "continueLessons": [
                lesson.to_camel_dict() for lesson in self.continue_lessons
            ],
        }
