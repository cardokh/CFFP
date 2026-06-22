"""
Learning item repository.

Responsibilities:
- Execute learning item database queries.
- Map database rows to domain objects.
- Persist and retrieve learning item data.
- Accept and return learning item domain objects at the repository boundary.

This repository isolates SQL/database access from the application layer.
"""

from backend.src.ccore.infrastructure.database import DatabaseManager
from src.modules.lla.learning_items.learning_item import LearningItem


class LearningItemRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _map_row_to_learning_item(self, row) -> LearningItem:
        return LearningItem(
            item_id=row[0],
            category_id=row[1],
            category_name=row[2],
            item_type=row[3],
            source_text=row[4],
            english_translation=row[5],
            pronunciation=row[6],
            example_text=row[7],
            is_active=bool(row[8]),
            created_at=row[9],
            updated_at=row[10],
            updated_by=row[11],
        )

    def find_by_id(self, learning_item: LearningItem) -> LearningItem | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                li.item_id,
                li.category_id,
                lc.name AS category_name,
                li.item_type,
                li.source_text,
                li.english_translation,
                li.pronunciation,
                li.example_text,
                li.is_active,
                li.created_at,
                li.updated_at,
                li.updated_by
            FROM learning_items li
            INNER JOIN lesson_categories lc
                ON li.category_id = lc.category_id
            WHERE li.item_id = ?
            """,
            (learning_item.item_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return self._map_row_to_learning_item(row)

    def find_by_source_text(self, learning_item: LearningItem) -> LearningItem | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                li.item_id,
                li.category_id,
                lc.name AS category_name,
                li.item_type,
                li.source_text,
                li.english_translation,
                li.pronunciation,
                li.example_text,
                li.is_active,
                li.created_at,
                li.updated_at,
                li.updated_by
            FROM learning_items li
            INNER JOIN lesson_categories lc
                ON li.category_id = lc.category_id
            WHERE li.source_text = ?
            """,
            (learning_item.source_text,),
        )

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return self._map_row_to_learning_item(row)

    def find_all_learning_items(self) -> list[LearningItem]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                li.item_id,
                li.category_id,
                lc.name AS category_name,
                li.item_type,
                li.source_text,
                li.english_translation,
                li.pronunciation,
                li.example_text,
                li.is_active,
                li.created_at,
                li.updated_at,
                li.updated_by
            FROM learning_items li
            INNER JOIN lesson_categories lc
                ON li.category_id = lc.category_id
            ORDER BY li.item_id
            """)

        rows = cursor.fetchall()
        conn.close()

        return [self._map_row_to_learning_item(row) for row in rows]

    def create_learning_item(
        self,
        learning_item: LearningItem,
    ) -> LearningItem:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO learning_items (
                category_id,
                item_type,
                source_text,
                english_translation,
                pronunciation,
                example_text,
                is_active,
                updated_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                learning_item.category_id,
                learning_item.item_type,
                learning_item.source_text,
                learning_item.english_translation,
                learning_item.pronunciation,
                learning_item.example_text,
                int(learning_item.is_active),
                learning_item.updated_by,
            ),
        )

        item_id = cursor.lastrowid

        conn.commit()
        conn.close()

        created_item = LearningItem(
            item_id=item_id,
            category_id=0,
            item_type="",
            source_text="",
            english_translation="",
            pronunciation=None,
            example_text=None,
            is_active=True,
        )

        return self.find_by_id(created_item)

    def update_learning_item(
        self,
        learning_item: LearningItem,
    ) -> LearningItem | None:
        existing_item = self.find_by_id(learning_item)

        if existing_item is None:
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE learning_items
            SET
                category_id = ?,
                item_type = ?,
                source_text = ?,
                english_translation = ?,
                pronunciation = ?,
                example_text = ?,
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE item_id = ?
            """,
            (
                learning_item.category_id,
                learning_item.item_type,
                learning_item.source_text,
                learning_item.english_translation,
                learning_item.pronunciation,
                learning_item.example_text,
                int(learning_item.is_active),
                learning_item.updated_by,
                learning_item.item_id,
            ),
        )

        conn.commit()
        conn.close()

        return self.find_by_id(learning_item)

    def delete_learning_item(self, learning_item: LearningItem) -> bool:
        existing_item = self.find_by_id(learning_item)

        if existing_item is None:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM learning_items
            WHERE item_id = ?
            """,
            (learning_item.item_id,),
        )

        conn.commit()
        conn.close()

        return True
