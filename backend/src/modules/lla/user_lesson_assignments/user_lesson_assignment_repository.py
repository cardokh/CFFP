"""
User lesson assignment repository.

Responsibilities:
- Handle persistence for user lesson assignments.
- Read assigned lessons for a user.
- Replace assigned lessons for a user.

Architecture:
service -> repository -> SQLite
"""

from src.core.infrastructure.database import DatabaseManager
from src.modules.lla.user_lesson_assignments.user_lesson_assignment_mapper import (
    UserLessonAssignmentMapper,
)


class UserLessonAssignmentRepository:
    def __init__(
        self,
        db_manager: DatabaseManager,
    ):
        self.db_manager = db_manager

    def get_user_lesson_assignments(
        self,
        request,
    ) -> list:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                ul.user_id,
                ul.lesson_id,
                ul.is_active,
                ul.assigned_at,
                ul.started_at,
                ul.completed_at,
                ul.updated_at,

                lst.lesson_status_type_id,
                lst.code AS lesson_status_code,
                lst.name AS lesson_status_name,

                l.title AS lesson_title,

                lc.category_id,
                lc.name AS category_name,

                lt.lesson_type_id,
                lt.name AS lesson_type_name,

                et.embodiment_type_id,
                et.name AS embodiment_type_name,

                ist.interaction_style_id,
                ist.name AS interaction_style_name

            FROM user_lessons ul

            INNER JOIN lesson_status_types lst
                ON ul.lesson_status_type_id = lst.lesson_status_type_id

            INNER JOIN lessons l
                ON ul.lesson_id = l.lesson_id

            INNER JOIN lesson_categories lc
                ON l.category_id = lc.category_id

            INNER JOIN lesson_types lt
                ON l.lesson_type_id = lt.lesson_type_id

            INNER JOIN embodiment_types et
                ON l.embodiment_type_id = et.embodiment_type_id

            INNER JOIN interaction_styles ist
                ON l.interaction_style_id = ist.interaction_style_id

            WHERE ul.user_id = ?

            ORDER BY l.lesson_id
            """,
            (request.user_id,),
        )

        rows = cursor.fetchall()

        conn.close()

        return [UserLessonAssignmentMapper.from_database_row(row) for row in rows]

    def get_student_lessons(
        self,
        request,
    ) -> list:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(ul.user_id, ?) AS user_id,
                l.lesson_id,
                COALESCE(ul.is_active, 0) AS is_active,
                ul.assigned_at,
                ul.started_at,
                ul.completed_at,
                ul.updated_at,

                lst.lesson_status_type_id,
                lst.code AS lesson_status_code,
                lst.name AS lesson_status_name,

                l.title AS lesson_title,

                lc.category_id,
                lc.name AS category_name,

                lt.lesson_type_id,
                lt.name AS lesson_type_name,

                et.embodiment_type_id,
                et.name AS embodiment_type_name,

                ist.interaction_style_id,
                ist.name AS interaction_style_name

            FROM lessons l

            LEFT JOIN user_lessons ul
                ON l.lesson_id = ul.lesson_id
               AND ul.user_id = ?

            LEFT JOIN lesson_status_types lst
                ON ul.lesson_status_type_id = lst.lesson_status_type_id

            INNER JOIN lesson_categories lc
                ON l.category_id = lc.category_id

            INNER JOIN lesson_types lt
                ON l.lesson_type_id = lt.lesson_type_id

            INNER JOIN embodiment_types et
                ON l.embodiment_type_id = et.embodiment_type_id

            INNER JOIN interaction_styles ist
                ON l.interaction_style_id = ist.interaction_style_id

            WHERE EXISTS (
                SELECT 1
                FROM lesson_learning_items lli
                WHERE lli.lesson_id = l.lesson_id
            )

            ORDER BY l.lesson_id
            """,
            (
                request.user_id,
                request.user_id,
            ),
        )

        rows = cursor.fetchall()

        conn.close()

        return [UserLessonAssignmentMapper.from_database_row(row) for row in rows]

    def replace_user_lesson_assignments(
        self,
        request,
    ) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM user_lessons
            WHERE user_id = ?
            """,
            (request.user_id,),
        )

        for lesson_id in request.lesson_ids:
            cursor.execute(
                """
                INSERT INTO user_lessons (
                    user_id,
                    lesson_id,
                    lesson_status_type_id,
                    is_active,
                    updated_by
                )
                VALUES (?, ?, 1, 1, 'system')
                """,
                (
                    request.user_id,
                    lesson_id,
                ),
            )

        conn.commit()
        conn.close()

    def mark_lesson_in_progress(
        self,
        request,
    ) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE user_lessons
            SET
                lesson_status_type_id = 2,
                started_at = COALESCE(started_at, CURRENT_TIMESTAMP),
                updated_at = CURRENT_TIMESTAMP,
                updated_by = 'system'
            WHERE user_id = ?
              AND lesson_id = ?
              AND lesson_status_type_id = 1
            """,
            (
                request.user_id,
                request.lesson_id,
            ),
        )

        conn.commit()
        conn.close()

    def mark_lesson_completed(
        self,
        request,
    ) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE user_lessons
            SET
                lesson_status_type_id = 3,
                started_at = COALESCE(started_at, CURRENT_TIMESTAMP),
                completed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = 'system'
            WHERE user_id = ?
              AND lesson_id = ?
            """,
            (
                request.user_id,
                request.lesson_id,
            ),
        )

        if request.score is not None and request.total_questions is not None:
            cursor.execute(
                """
                INSERT INTO lesson_results (
                    user_id,
                    lesson_id,
                    score,
                    total_questions,
                    completed_at
                )
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    request.user_id,
                    request.lesson_id,
                    request.score,
                    request.total_questions,
                ),
            )

        conn.commit()
        conn.close()

    def signup_student_lesson(
        self,
        request,
    ) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO user_lessons (
                user_id,
                lesson_id,
                lesson_status_type_id,
                is_active,
                updated_by
            )
            VALUES (?, ?, 1, 1, 'system')
            """,
            (
                request.user_id,
                request.lesson_id,
            ),
        )

        conn.commit()
        conn.close()

    def remove_student_lesson(
        self,
        request,
    ) -> None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM user_lessons
            WHERE user_id = ?
              AND lesson_id = ?
            """,
            (
                request.user_id,
                request.lesson_id,
            ),
        )

        conn.commit()
        conn.close()
