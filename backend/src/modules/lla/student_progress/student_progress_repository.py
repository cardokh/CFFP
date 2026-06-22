"""
Student progress repository.

Responsibilities:
- Read student progress data from existing database tables.
- Keep SQL/database access isolated from the application layer.
- Return student progress domain objects.

Architecture:
Service -> Repository -> SQLite
"""

from backend.src.ccore.infrastructure.database import DatabaseManager
from src.modules.lla.student_progress.student_progress import (
    StudentProgressLesson,
    StudentProgressOverview,
    StudentProgressSummary,
)

COMPLETED_STATUS_CODE = "COMPLETED"
IN_PROGRESS_STATUS_CODE = "IN_PROGRESS"
NOT_STARTED_STATUS_CODE = "NOT_STARTED"


class StudentProgressRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @staticmethod
    def _map_row_to_progress_lesson(row) -> StudentProgressLesson:
        return StudentProgressLesson(
            lesson_id=row[0],
            lesson_title=row[1],
            category_name=row[2],
            lesson_type_name=row[3],
            lesson_status_code=row[4],
            lesson_status_name=row[5],
            assigned_at=row[6],
            started_at=row[7],
            completed_at=row[8],
            score=row[9],
            total_questions=row[10],
        )

    def get_student_progress_overview(
        self,
        user_id: int,
    ) -> StudentProgressOverview:
        progress_lessons = self._get_student_progress_lessons(user_id)

        total_lessons = len(progress_lessons)

        completed_lessons = [
            lesson
            for lesson in progress_lessons
            if lesson.lesson_status_code == COMPLETED_STATUS_CODE
        ]

        in_progress_lessons = [
            lesson
            for lesson in progress_lessons
            if lesson.lesson_status_code == IN_PROGRESS_STATUS_CODE
        ]

        not_started_lessons = [
            lesson
            for lesson in progress_lessons
            if lesson.lesson_status_code == NOT_STARTED_STATUS_CODE
        ]

        continue_lessons = [
            lesson
            for lesson in progress_lessons
            if lesson.lesson_status_code != COMPLETED_STATUS_CODE
        ]

        completion_percentage = 0.0

        if total_lessons > 0:
            completion_percentage = round(
                (len(completed_lessons) / total_lessons) * 100,
                1,
            )

        summary = StudentProgressSummary(
            total_lessons=total_lessons,
            completed_lessons=len(completed_lessons),
            in_progress_lessons=len(in_progress_lessons),
            not_started_lessons=len(not_started_lessons),
            completion_percentage=completion_percentage,
        )

        return StudentProgressOverview(
            summary=summary,
            completed_lessons=completed_lessons,
            continue_lessons=continue_lessons,
        )

    def _get_student_progress_lessons(
        self,
        user_id: int,
    ) -> list[StudentProgressLesson]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                l.lesson_id,
                l.title AS lesson_title,
                lc.name AS category_name,
                lt.name AS lesson_type_name,
                lst.code AS lesson_status_code,
                lst.name AS lesson_status_name,
                ul.assigned_at,
                ul.started_at,
                ul.completed_at,
                latest_result.score,
                latest_result.total_questions

            FROM user_lessons ul

            INNER JOIN lessons l
                ON ul.lesson_id = l.lesson_id

            INNER JOIN lesson_categories lc
                ON l.category_id = lc.category_id

            INNER JOIN lesson_types lt
                ON l.lesson_type_id = lt.lesson_type_id

            INNER JOIN lesson_status_types lst
                ON ul.lesson_status_type_id = lst.lesson_status_type_id

            LEFT JOIN lesson_results latest_result
                ON latest_result.result_id = (
                    SELECT lr.result_id
                    FROM lesson_results lr
                    WHERE lr.user_id = ul.user_id
                      AND lr.lesson_id = ul.lesson_id
                    ORDER BY lr.completed_at DESC, lr.result_id DESC
                    LIMIT 1
                )

            WHERE ul.user_id = ?
              AND ul.is_active = 1
              AND l.is_active = 1

            ORDER BY
                ul.completed_at IS NULL,
                ul.completed_at DESC,
                ul.started_at DESC,
                ul.assigned_at DESC,
                l.lesson_id
            """,
            (user_id,),
        )

        rows = cursor.fetchall()

        conn.close()

        return [self._map_row_to_progress_lesson(row) for row in rows]
