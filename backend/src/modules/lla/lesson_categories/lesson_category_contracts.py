"""
Lesson category contracts.

Responsibilities:
- Define request and response structures for lesson category use cases.
- Keep API/service boundaries explicit and reusable.
- Centralize input normalization for lesson category create/update operations.
- Centralize API-friendly response serialization.

Architecture:
API -> Contracts -> LessonCategoryService -> LessonCategoryRepository -> SQLite Database

Notes:
- These contracts are not domain objects.
- Domain objects represent internal business entities.
- Contracts represent boundary data moving into or out of use cases.
"""

from dataclasses import dataclass

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.lesson_categories.lesson_category import LessonCategory

SYSTEM_UPDATED_BY = "system"


@dataclass(frozen=True)
class CreateLessonCategoryRequest:
    name: str
    description: str | None
    is_active: bool
    updated_by: str | None = None

    @property
    def cleaned_name(self) -> str:
        return self.name.strip() if self.name else ""

    @property
    def cleaned_description(self) -> str | None:
        return self.description.strip() if self.description else None

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class UpdateLessonCategoryRequest:
    category_id: int
    name: str
    description: str | None
    is_active: bool
    updated_by: str | None = None

    @property
    def cleaned_name(self) -> str:
        return self.name.strip() if self.name else ""

    @property
    def cleaned_description(self) -> str | None:
        return self.description.strip() if self.description else None

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class LessonCategoryDetails:
    category_id: int | None
    name: str
    description: str | None
    is_active: bool
    created_at: str | None
    updated_at: str | None
    updated_by: str | None

    @classmethod
    def from_domain(cls, lesson_category: LessonCategory):
        return cls(
            category_id=lesson_category.category_id,
            name=lesson_category.name,
            description=lesson_category.description,
            is_active=lesson_category.is_active,
            created_at=lesson_category.created_at,
            updated_at=lesson_category.updated_at,
            updated_by=lesson_category.updated_by,
        )

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())


LessonCategorySummary = LessonCategoryDetails
