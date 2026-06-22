"""
Lesson repository.

Responsibilities:
- Execute lesson database queries.
- Map database rows to lesson domain objects.
- Persist and retrieve lesson data.
- Accept and return lesson domain objects at the repository boundary.

This repository isolates lesson SQL/database access from the application layer.
"""

from backend.src.ccore.infrastructure.database import DatabaseManager
from src.modules.lla.lessons.lesson import Lesson


class LessonRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _map_row_to_lesson(self, row) -> Lesson:
        return Lesson(
            lesson_id=row[0],
            category_id=row[1],
            lesson_type_id=row[2],
            embodiment_type_id=row[3],
            interaction_style_id=row[4],
            title=row[5],
            description=row[6],
            is_active=bool(row[7]),
            category_name=row[8],
            lesson_type_name=row[9],
            embodiment_type_name=row[10],
            interaction_style_name=row[11],
            learning_items_count=row[12],
            quiz_questions_count=row[13],
            created_at=row[14],
            updated_at=row[15],
            updated_by=row[16],
        )

    def find_by_id(
        self,
        lesson: Lesson,
    ) -> Lesson | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                l.lesson_id,
                l.category_id,
                l.lesson_type_id,
                l.embodiment_type_id,
                l.interaction_style_id,
                l.title,
                l.description,
                l.is_active,

                lc.name AS category_name,
                lt.name AS lesson_type_name,
                et.name AS embodiment_type_name,
                ist.name AS interaction_style_name,

                (
                    SELECT COUNT(*)
                    FROM lesson_learning_items lli
                    WHERE lli.lesson_id = l.lesson_id
                ) AS learning_items_count,

                (
                    SELECT COUNT(*)
                    FROM lesson_quiz_questions lqq
                    WHERE lqq.lesson_id = l.lesson_id
                ) AS quiz_questions_count,

                l.created_at,
                l.updated_at,
                l.updated_by

            FROM lessons l

            INNER JOIN lesson_categories lc
                ON l.category_id = lc.category_id

            INNER JOIN lesson_types lt
                ON l.lesson_type_id = lt.lesson_type_id

            INNER JOIN embodiment_types et
                ON l.embodiment_type_id = et.embodiment_type_id

            INNER JOIN interaction_styles ist
                ON l.interaction_style_id = ist.interaction_style_id

            WHERE l.lesson_id = ?
            """,
            (lesson.lesson_id,),
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:
            return None

        return self._map_row_to_lesson(row)

    def find_all_lessons(self) -> list[Lesson]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                l.lesson_id,
                l.category_id,
                l.lesson_type_id,
                l.embodiment_type_id,
                l.interaction_style_id,
                l.title,
                l.description,
                l.is_active,

                lc.name AS category_name,
                lt.name AS lesson_type_name,
                et.name AS embodiment_type_name,
                ist.name AS interaction_style_name,

                (
                    SELECT COUNT(*)
                    FROM lesson_learning_items lli
                    WHERE lli.lesson_id = l.lesson_id
                ) AS learning_items_count,

                (
                    SELECT COUNT(*)
                    FROM lesson_quiz_questions lqq
                    WHERE lqq.lesson_id = l.lesson_id
                ) AS quiz_questions_count,

                l.created_at,
                l.updated_at,
                l.updated_by

            FROM lessons l

            INNER JOIN lesson_categories lc
                ON l.category_id = lc.category_id

            INNER JOIN lesson_types lt
                ON l.lesson_type_id = lt.lesson_type_id

            INNER JOIN embodiment_types et
                ON l.embodiment_type_id = et.embodiment_type_id

            INNER JOIN interaction_styles ist
                ON l.interaction_style_id = ist.interaction_style_id

            ORDER BY l.lesson_id
            """)

        rows = cursor.fetchall()

        conn.close()

        return [self._map_row_to_lesson(row) for row in rows]

    def create_lesson(
        self,
        lesson: Lesson,
    ) -> Lesson:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO lessons (
                category_id,
                lesson_type_id,
                embodiment_type_id,
                interaction_style_id,
                title,
                description,
                is_active,
                updated_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lesson.category_id,
                lesson.lesson_type_id,
                lesson.embodiment_type_id,
                lesson.interaction_style_id,
                lesson.title,
                lesson.description,
                int(lesson.is_active),
                lesson.updated_by,
            ),
        )

        lesson_id = cursor.lastrowid

        conn.commit()
        conn.close()

        created_lesson = Lesson(
            lesson_id=lesson_id,
            category_id=0,
            lesson_type_id=0,
            embodiment_type_id=0,
            interaction_style_id=0,
            title="",
            description=None,
            is_active=True,
        )

        return self.find_by_id(created_lesson)

    def update_lesson(
        self,
        lesson: Lesson,
    ) -> Lesson | None:
        existing_lesson = self.find_by_id(lesson)

        if existing_lesson is None:
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE lessons
            SET
                category_id = ?,
                lesson_type_id = ?,
                embodiment_type_id = ?,
                interaction_style_id = ?,
                title = ?,
                description = ?,
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE lesson_id = ?
            """,
            (
                lesson.category_id,
                lesson.lesson_type_id,
                lesson.embodiment_type_id,
                lesson.interaction_style_id,
                lesson.title,
                lesson.description,
                int(lesson.is_active),
                lesson.updated_by,
                lesson.lesson_id,
            ),
        )

        conn.commit()
        conn.close()

        return self.find_by_id(lesson)

    def delete_lesson(
        self,
        lesson: Lesson,
    ) -> bool:
        existing_lesson = self.find_by_id(lesson)

        if existing_lesson is None:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM lessons
            WHERE lesson_id = ?
            """,
            (lesson.lesson_id,),
        )

        conn.commit()
        conn.close()

        return True
