"""
Lesson category repository.

Responsibilities:
- Execute lesson category database queries.
- Map database rows to domain objects.
- Persist and retrieve lesson category data.
- Accept and return lesson category domain objects at the repository boundary.

This repository isolates SQL/database access from the application layer.
"""

from src.core.infrastructure.database import DatabaseManager
from src.modules.lla.lesson_categories.lesson_category import LessonCategory


class LessonCategoryRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _map_row_to_lesson_category(self, row) -> LessonCategory:
        return LessonCategory(
            category_id=row[0],
            name=row[1],
            description=row[2],
            is_active=bool(row[3]),
            created_at=row[4],
            updated_at=row[5],
            updated_by=row[6],
        )

    def find_by_id(self, lesson_category: LessonCategory) -> LessonCategory | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                category_id,
                name,
                description,
                is_active,
                created_at,
                updated_at,
                updated_by
            FROM lesson_categories
            WHERE category_id = ?
            """,
            (lesson_category.category_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return self._map_row_to_lesson_category(row)

    def find_by_name(self, lesson_category: LessonCategory) -> LessonCategory | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                category_id,
                name,
                description,
                is_active,
                created_at,
                updated_at,
                updated_by
            FROM lesson_categories
            WHERE name = ?
            """,
            (lesson_category.name,),
        )

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return self._map_row_to_lesson_category(row)

    def find_all_lesson_categories(self) -> list[LessonCategory]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                category_id,
                name,
                description,
                is_active,
                created_at,
                updated_at,
                updated_by
            FROM lesson_categories
            ORDER BY category_id
            """)

        rows = cursor.fetchall()
        conn.close()

        return [self._map_row_to_lesson_category(row) for row in rows]

    def create_lesson_category(
        self,
        lesson_category: LessonCategory,
    ) -> LessonCategory:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO lesson_categories (
                name,
                description,
                is_active,
                updated_by
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                lesson_category.name,
                lesson_category.description,
                int(lesson_category.is_active),
                lesson_category.updated_by,
            ),
        )

        category_id = cursor.lastrowid

        conn.commit()
        conn.close()

        created_category = LessonCategory(
            category_id=category_id,
            name=lesson_category.name,
            description=lesson_category.description,
            is_active=lesson_category.is_active,
            updated_by=lesson_category.updated_by,
        )

        return self.find_by_id(created_category)

    def update_lesson_category(
        self,
        lesson_category: LessonCategory,
    ) -> LessonCategory | None:
        existing_category = self.find_by_id(lesson_category)

        if existing_category is None:
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE lesson_categories
            SET
                name = ?,
                description = ?,
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE category_id = ?
            """,
            (
                lesson_category.name,
                lesson_category.description,
                int(lesson_category.is_active),
                lesson_category.updated_by,
                lesson_category.category_id,
            ),
        )

        conn.commit()
        conn.close()

        return self.find_by_id(lesson_category)

    def delete_lesson_category(self, lesson_category: LessonCategory) -> bool:
        existing_category = self.find_by_id(lesson_category)

        if existing_category is None:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM lesson_categories
            WHERE category_id = ?
            """,
            (lesson_category.category_id,),
        )

        conn.commit()
        conn.close()

        return True
