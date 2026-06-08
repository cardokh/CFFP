"""
Quiz question option repository.

Responsibilities:
- Execute quiz question option database queries.
- Persist and retrieve quiz question option data.
- Map database rows to QuizQuestionOption domain objects.
- Keep SQL/database access isolated from the application layer.

Architecture:
Service -> Repository -> SQLite
"""

from src.core.infrastructure.database import DatabaseManager
from src.modules.lla.quiz_questions.quiz_question_option import (
    QuizQuestionOption,
)


class QuizQuestionOptionRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @staticmethod
    def _map_row_to_quiz_question_option(
        row,
    ) -> QuizQuestionOption:
        return QuizQuestionOption(
            option_id=row[0],
            question_id=row[1],
            option_text=row[2],
            is_correct=bool(row[3]),
            display_order=row[4],
            created_at=row[5],
            updated_at=row[6],
            updated_by=row[7],
        )

    def find_by_id(
        self,
        quiz_question_option: QuizQuestionOption,
    ) -> QuizQuestionOption | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                option_id,
                question_id,
                option_text,
                is_correct,
                display_order,
                created_at,
                updated_at,
                updated_by
            FROM quiz_question_options
            WHERE option_id = ?
            """,
            (quiz_question_option.option_id,),
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:
            return None

        return self._map_row_to_quiz_question_option(row)

    def find_by_question_id(
        self,
        question_id: int,
    ) -> list[QuizQuestionOption]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                option_id,
                question_id,
                option_text,
                is_correct,
                display_order,
                created_at,
                updated_at,
                updated_by
            FROM quiz_question_options
            WHERE question_id = ?
            ORDER BY display_order
            """,
            (question_id,),
        )

        rows = cursor.fetchall()

        conn.close()

        return [self._map_row_to_quiz_question_option(row) for row in rows]

    def create_quiz_question_option(
        self,
        quiz_question_option: QuizQuestionOption,
    ) -> QuizQuestionOption:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO quiz_question_options (
                question_id,
                option_text,
                is_correct,
                display_order,
                updated_by
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                quiz_question_option.question_id,
                quiz_question_option.option_text,
                int(quiz_question_option.is_correct),
                quiz_question_option.display_order,
                quiz_question_option.updated_by,
            ),
        )

        option_id = cursor.lastrowid

        conn.commit()
        conn.close()

        created_option = QuizQuestionOption(
            option_id=option_id,
            question_id=quiz_question_option.question_id,
            option_text="",
            is_correct=False,
            display_order=1,
        )

        return self.find_by_id(created_option)

    def update_quiz_question_option(
        self,
        quiz_question_option: QuizQuestionOption,
    ) -> QuizQuestionOption | None:
        existing_option = self.find_by_id(quiz_question_option)

        if existing_option is None:
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE quiz_question_options
            SET
                option_text = ?,
                is_correct = ?,
                display_order = ?,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE option_id = ?
            """,
            (
                quiz_question_option.option_text,
                int(quiz_question_option.is_correct),
                quiz_question_option.display_order,
                quiz_question_option.updated_by,
                quiz_question_option.option_id,
            ),
        )

        conn.commit()
        conn.close()

        return self.find_by_id(quiz_question_option)

    def delete_quiz_question_option(
        self,
        quiz_question_option: QuizQuestionOption,
    ) -> bool:
        existing_option = self.find_by_id(quiz_question_option)

        if existing_option is None:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM quiz_question_options
            WHERE option_id = ?
            """,
            (quiz_question_option.option_id,),
        )

        conn.commit()
        conn.close()

        return True

    def replace_question_options(
        self,
        question_id: int,
        quiz_question_options: list[QuizQuestionOption],
    ) -> list[QuizQuestionOption]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM quiz_question_options
            WHERE question_id = ?
            """,
            (question_id,),
        )

        for quiz_question_option in quiz_question_options:
            cursor.execute(
                """
                INSERT INTO quiz_question_options (
                    question_id,
                    option_text,
                    is_correct,
                    display_order,
                    updated_by
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    quiz_question_option.question_id,
                    quiz_question_option.option_text,
                    int(quiz_question_option.is_correct),
                    quiz_question_option.display_order,
                    quiz_question_option.updated_by,
                ),
            )

        conn.commit()
        conn.close()

        return self.find_by_question_id(question_id)
