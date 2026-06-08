"""
Lesson quiz question assignment repository.

Responsibilities:
- Read and replace ordered quiz question assignments for a lesson.
- Persist assignment rows in lesson_quiz_questions.
- Return assignment domain objects.
"""

from src.core.infrastructure.database import DatabaseManager
from src.modules.lla.lessons.lesson_quiz_question_assignment import (
    LessonQuizQuestionAssignment,
)


class LessonQuizQuestionAssignmentRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @staticmethod
    def _map_row_to_assignment(row) -> LessonQuizQuestionAssignment:
        return LessonQuizQuestionAssignment(
            lesson_id=row[0],
            question_id=row[1],
            display_order=row[2],
            question_text=row[3],
            category_id=row[4],
            category_name=row[5],
            is_active=bool(row[6]),
        )

    def find_by_lesson_id(
        self,
        lesson_id: int,
    ) -> list[LessonQuizQuestionAssignment]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                lqq.lesson_id,
                lqq.question_id,
                lqq.display_order,
                qq.question_text,
                qq.category_id,
                lc.name AS category_name,
                qq.is_active
            FROM lesson_quiz_questions lqq
            INNER JOIN quiz_questions qq
                ON lqq.question_id = qq.question_id
            INNER JOIN lesson_categories lc
                ON qq.category_id = lc.category_id
            WHERE lqq.lesson_id = ?
            ORDER BY lqq.display_order
            """,
            (lesson_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [self._map_row_to_assignment(row) for row in rows]

    def replace_lesson_quiz_questions(
        self,
        lesson_id: int,
        assignments: list[LessonQuizQuestionAssignment],
    ) -> list[LessonQuizQuestionAssignment]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM lesson_quiz_questions
            WHERE lesson_id = ?
            """,
            (lesson_id,),
        )

        for assignment in assignments:
            cursor.execute(
                """
                INSERT INTO lesson_quiz_questions (
                    lesson_id,
                    question_id,
                    display_order
                )
                VALUES (?, ?, ?)
                """,
                (
                    assignment.lesson_id,
                    assignment.question_id,
                    assignment.display_order,
                ),
            )

        conn.commit()
        conn.close()

        return self.find_by_lesson_id(lesson_id)
