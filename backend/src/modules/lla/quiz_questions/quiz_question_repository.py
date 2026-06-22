"""
Quiz question repository.

Responsibilities:
- Execute quiz question database queries.
- Map database rows to quiz question domain objects.
- Persist and retrieve quiz question data.
- Accept and return quiz question domain objects at the repository boundary.

This repository isolates quiz question SQL/database access from the application layer.

Note:
Quiz question options are owned by QuizQuestionOptionRepository.
"""

from backend.src.ccore.infrastructure.database import DatabaseManager
from src.modules.lla.quiz_questions.quiz_question import QuizQuestion


class QuizQuestionRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _map_row_to_quiz_question(self, row) -> QuizQuestion:
        return QuizQuestion(
            question_id=row[0],
            category_id=row[1],
            category_name=row[2],
            question_text=row[3],
            is_active=bool(row[4]),
            created_at=row[5],
            updated_at=row[6],
            updated_by=row[7],
        )

    def find_by_id(self, quiz_question: QuizQuestion) -> QuizQuestion | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                qq.question_id,
                qq.category_id,
                lc.name AS category_name,
                qq.question_text,
                qq.is_active,
                qq.created_at,
                qq.updated_at,
                qq.updated_by
            FROM quiz_questions qq
            INNER JOIN lesson_categories lc
                ON qq.category_id = lc.category_id
            WHERE qq.question_id = ?
            """,
            (quiz_question.question_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return self._map_row_to_quiz_question(row)

    def find_by_question_text(
        self,
        quiz_question: QuizQuestion,
    ) -> QuizQuestion | None:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                qq.question_id,
                qq.category_id,
                lc.name AS category_name,
                qq.question_text,
                qq.is_active,
                qq.created_at,
                qq.updated_at,
                qq.updated_by
            FROM quiz_questions qq
            INNER JOIN lesson_categories lc
                ON qq.category_id = lc.category_id
            WHERE qq.question_text = ?
            """,
            (quiz_question.question_text,),
        )

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return self._map_row_to_quiz_question(row)

    def find_all_quiz_questions(self) -> list[QuizQuestion]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                qq.question_id,
                qq.category_id,
                lc.name AS category_name,
                qq.question_text,
                qq.is_active,
                qq.created_at,
                qq.updated_at,
                qq.updated_by
            FROM quiz_questions qq
            INNER JOIN lesson_categories lc
                ON qq.category_id = lc.category_id
            ORDER BY qq.question_id
            """)

        rows = cursor.fetchall()
        conn.close()

        return [self._map_row_to_quiz_question(row) for row in rows]

    def create_quiz_question(
        self,
        quiz_question: QuizQuestion,
    ) -> QuizQuestion:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO quiz_questions (
                category_id,
                question_text,
                is_active,
                updated_by
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                quiz_question.category_id,
                quiz_question.question_text,
                int(quiz_question.is_active),
                quiz_question.updated_by,
            ),
        )

        question_id = cursor.lastrowid

        conn.commit()
        conn.close()

        created_question = QuizQuestion(
            question_id=question_id,
            category_id=0,
            question_text="",
            is_active=True,
        )

        return self.find_by_id(created_question)

    def update_quiz_question(
        self,
        quiz_question: QuizQuestion,
    ) -> QuizQuestion | None:
        existing_question = self.find_by_id(quiz_question)

        if existing_question is None:
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE quiz_questions
            SET
                category_id = ?,
                question_text = ?,
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE question_id = ?
            """,
            (
                quiz_question.category_id,
                quiz_question.question_text,
                int(quiz_question.is_active),
                quiz_question.updated_by,
                quiz_question.question_id,
            ),
        )

        conn.commit()
        conn.close()

        return self.find_by_id(quiz_question)

    def delete_quiz_question(self, quiz_question: QuizQuestion) -> bool:
        existing_question = self.find_by_id(quiz_question)

        if existing_question is None:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM quiz_questions
            WHERE question_id = ?
            """,
            (quiz_question.question_id,),
        )

        conn.commit()
        conn.close()

        return True
