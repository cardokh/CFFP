"""
Reference data repository.

Responsibilities:
- Retrieve stable lookup/reference data used by admin forms
- Keep dropdown/reference queries separate from CRUD repositories
- Provide simple API-friendly dictionaries for small lookup tables
"""

from src.core.infrastructure.database import DatabaseManager


class ReferenceDataRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _find_all_simple_lookup(
        self,
        table_name: str,
        id_column: str,
        name_column: str,
    ) -> list[dict]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT
                {id_column},
                {name_column}
            FROM {table_name}
            WHERE is_active = 1
            ORDER BY {name_column}
            """)

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "name": row[1],
            }
            for row in rows
        ]

    def find_active_lesson_categories(self) -> list[dict]:
        return self._find_all_simple_lookup(
            table_name="lesson_categories",
            id_column="category_id",
            name_column="name",
        )

    def find_active_lesson_types(self) -> list[dict]:
        return self._find_all_simple_lookup(
            table_name="lesson_types",
            id_column="lesson_type_id",
            name_column="name",
        )

    def find_active_embodiment_types(self) -> list[dict]:
        return self._find_all_simple_lookup(
            table_name="embodiment_types",
            id_column="embodiment_type_id",
            name_column="name",
        )

    def find_active_interaction_styles(self) -> list[dict]:
        return self._find_all_simple_lookup(
            table_name="interaction_styles",
            id_column="interaction_style_id",
            name_column="name",
        )
