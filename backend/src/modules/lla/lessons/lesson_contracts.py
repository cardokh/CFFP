"""
Lesson contracts.

Responsibilities:
- Define request and response structures for lesson use cases.
- Keep API/service boundaries explicit and reusable.
- Centralize input normalization for lesson create/update operations.
- Centralize API-friendly response serialization.

Architecture:
API -> Contracts -> LessonService -> LessonRepository -> SQLite Database

Notes:
- These contracts are not domain objects.
- Domain objects represent internal business entities.
- Contracts represent boundary data moving into or out of use cases.
- The current Lessons Admin frontend expects snake_case response fields.
"""

from dataclasses import dataclass

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.lessons.lesson import Lesson

SYSTEM_UPDATED_BY = "system"


@dataclass(frozen=True)
class CreateLessonRequest:
    category_id: int
    lesson_type_id: int
    embodiment_type_id: int
    interaction_style_id: int
    title: str
    description: str | None
    is_active: bool
    updated_by: str | None = None

    @property
    def cleaned_title(self) -> str:
        return self.title.strip() if self.title else ""

    @property
    def cleaned_description(self) -> str | None:
        return self.description.strip() if self.description else None

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class UpdateLessonRequest:
    lesson_id: int
    category_id: int
    lesson_type_id: int
    embodiment_type_id: int
    interaction_style_id: int
    title: str
    description: str | None
    is_active: bool
    updated_by: str | None = None

    @property
    def cleaned_title(self) -> str:
        return self.title.strip() if self.title else ""

    @property
    def cleaned_description(self) -> str | None:
        return self.description.strip() if self.description else None

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class LessonDetails:
    lesson_id: int | None
    category_id: int
    lesson_type_id: int
    embodiment_type_id: int
    interaction_style_id: int
    title: str
    description: str | None
    is_active: bool
    category_name: str | None
    lesson_type_name: str | None
    embodiment_type_name: str | None
    interaction_style_name: str | None
    learning_items_count: int
    quiz_questions_count: int
    created_at: str | None
    updated_at: str | None
    updated_by: str | None

    @classmethod
    def from_domain(cls, lesson: Lesson):
        return cls(
            lesson_id=lesson.lesson_id,
            category_id=lesson.category_id,
            lesson_type_id=lesson.lesson_type_id,
            embodiment_type_id=lesson.embodiment_type_id,
            interaction_style_id=lesson.interaction_style_id,
            title=lesson.title,
            description=lesson.description,
            is_active=lesson.is_active,
            category_name=lesson.category_name,
            lesson_type_name=lesson.lesson_type_name,
            embodiment_type_name=lesson.embodiment_type_name,
            interaction_style_name=lesson.interaction_style_name,
            learning_items_count=lesson.learning_items_count,
            quiz_questions_count=lesson.quiz_questions_count,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
            updated_by=lesson.updated_by,
        )

    def to_dict(self):
        return {
            "lesson_id": self.lesson_id,
            "category_id": self.category_id,
            "lesson_type_id": self.lesson_type_id,
            "embodiment_type_id": self.embodiment_type_id,
            "interaction_style_id": self.interaction_style_id,
            "title": self.title,
            "description": self.description,
            "is_active": self.is_active,
            "category_name": self.category_name,
            "lesson_type_name": self.lesson_type_name,
            "embodiment_type_name": self.embodiment_type_name,
            "interaction_style_name": self.interaction_style_name,
            "learning_items_count": self.learning_items_count,
            "quiz_questions_count": self.quiz_questions_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())


LessonSummary = LessonDetails
