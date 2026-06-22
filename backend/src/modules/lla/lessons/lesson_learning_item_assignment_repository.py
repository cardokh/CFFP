"""
Lesson learning item assignment repository.

Responsibilities:
- Read and replace ordered learning item assignments for a lesson.
- Persist assignment rows in lesson_learning_items.
- Return assignment domain objects.
"""

from backend.src.ccore.infrastructure.database import DatabaseManager
from src.modules.lla.lessons.lesson_learning_item_assignment import (
    LessonLearningItemAssignment,
)


class LessonLearningItemAssignmentRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @staticmethod
    def _map_row_to_assignment(row) -> LessonLearningItemAssignment:
        return LessonLearningItemAssignment(
            lesson_id=row[0],
            item_id=row[1],
            display_order=row[2],
            source_text=row[3],
            english_translation=row[4],
            pronunciation=row[5],
            example_text=row[6],
            item_type=row[7],
        )

    def find_by_lesson_id(
        self,
        lesson_id: int,
    ) -> list[LessonLearningItemAssignment]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                lli.lesson_id,
                lli.item_id,
                lli.display_order,
                li.source_text,
                li.english_translation,
                li.pronunciation,
                li.example_text,
                li.item_type
            FROM lesson_learning_items lli
            INNER JOIN learning_items li
                ON lli.item_id = li.item_id
            WHERE lli.lesson_id = ?
            ORDER BY lli.display_order
            """,
            (lesson_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [self._map_row_to_assignment(row) for row in rows]

    def replace_lesson_learning_items(
        self,
        lesson_id: int,
        assignments: list[LessonLearningItemAssignment],
    ) -> list[LessonLearningItemAssignment]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM lesson_learning_items
            WHERE lesson_id = ?
            """,
            (lesson_id,),
        )

        for assignment in assignments:
            cursor.execute(
                """
                INSERT INTO lesson_learning_items (
                    lesson_id,
                    item_id,
                    display_order
                )
                VALUES (?, ?, ?)
                """,
                (
                    assignment.lesson_id,
                    assignment.item_id,
                    assignment.display_order,
                ),
            )

        conn.commit()
        conn.close()

        return self.find_by_lesson_id(lesson_id)
