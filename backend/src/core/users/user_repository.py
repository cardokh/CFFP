"""
User repository.

Responsibilities:
- Execute user-related database queries
- Map database rows to domain objects
- Persist and retrieve user data

This repository isolates SQL/database access from the application layer.
"""

from src.core.infrastructure.database import DatabaseManager
from src.core.users.user import User


class UserRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _map_row_to_user(self, row) -> User:
        return User(
            user_id=row[0],
            display_name=row[1],
            email=row[2],
            password_hash=row[3],
            is_active=bool(row[4]),
            is_verified=bool(row[5]),
            is_admin=bool(row[6]),
            created_at=row[7],
        )

    def find_by_email(self, email: str) -> User | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                user_id,
                display_name,
                email,
                password_hash,
                is_active,
                is_verified,
                is_admin,
                created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:
            return None

        return self._map_row_to_user(row)

    def find_by_id(self, user_id: int) -> User | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                user_id,
                display_name,
                email,
                password_hash,
                is_active,
                is_verified,
                is_admin,
                created_at
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:
            return None

        return self._map_row_to_user(row)

    def find_all_users(self) -> list[User]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                user_id,
                display_name,
                email,
                password_hash,
                is_active,
                is_verified,
                is_admin,
                created_at
            FROM users
            ORDER BY user_id
            """)

        rows = cursor.fetchall()

        conn.close()

        return [self._map_row_to_user(row) for row in rows]

    def create_user(self, user: User) -> User:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users (
                display_name,
                email,
                password_hash,
                is_active,
                is_verified,
                is_admin
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user.display_name,
                user.email,
                user.password_hash,
                int(user.is_active),
                int(user.is_verified),
                int(user.is_admin),
            ),
        )

        user_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return self.find_by_id(user_id)

    def update_user_basic_info(
        self,
        user_id: int,
        display_name: str,
        email: str,
        is_active: bool,
        is_verified: bool,
        is_admin: bool,
    ) -> User | None:
        existing_user = self.find_by_id(user_id)

        if existing_user is None:
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET
                display_name = ?,
                email = ?,
                is_active = ?,
                is_verified = ?,
                is_admin = ?
            WHERE user_id = ?
            """,
            (
                display_name,
                email,
                int(is_active),
                int(is_verified),
                int(is_admin),
                user_id,
            ),
        )

        conn.commit()
        conn.close()

        return self.find_by_id(user_id)

    def delete_user_by_id(self, user_id: int) -> bool:
        existing_user = self.find_by_id(user_id)

        if existing_user is None:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

        conn.commit()
        conn.close()

        return True
