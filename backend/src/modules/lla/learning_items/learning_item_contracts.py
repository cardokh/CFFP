"""
Learning item contracts.

Responsibilities:
- Define request and response structures for learning item use cases.
- Keep API/service boundaries explicit and reusable.
- Centralize input normalization for learning item create/update operations.
- Centralize API-friendly response serialization.

Architecture:
API -> Contracts -> LearningItemService -> LearningItemRepository -> SQLite Database

Notes:
- These contracts are not domain objects.
- Domain objects represent internal business entities.
- Contracts represent boundary data moving into or out of use cases.
"""

from dataclasses import dataclass

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.learning_items.learning_item import LearningItem

SYSTEM_UPDATED_BY = "system"


@dataclass(frozen=True)
class CreateLearningItemRequest:
    category_id: int
    item_type: str
    source_text: str
    english_translation: str
    pronunciation: str | None
    example_text: str | None
    is_active: bool
    updated_by: str | None = None

    @property
    def cleaned_item_type(self) -> str:
        return self.item_type.strip().lower() if self.item_type else ""

    @property
    def cleaned_source_text(self) -> str:
        return self.source_text.strip() if self.source_text else ""

    @property
    def cleaned_english_translation(self) -> str:
        return self.english_translation.strip() if self.english_translation else ""

    @property
    def cleaned_pronunciation(self) -> str | None:
        return self.pronunciation.strip() if self.pronunciation else None

    @property
    def cleaned_example_text(self) -> str | None:
        return self.example_text.strip() if self.example_text else None

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class UpdateLearningItemRequest:
    item_id: int
    category_id: int
    item_type: str
    source_text: str
    english_translation: str
    pronunciation: str | None
    example_text: str | None
    is_active: bool
    updated_by: str | None = None

    @property
    def cleaned_item_type(self) -> str:
        return self.item_type.strip().lower() if self.item_type else ""

    @property
    def cleaned_source_text(self) -> str:
        return self.source_text.strip() if self.source_text else ""

    @property
    def cleaned_english_translation(self) -> str:
        return self.english_translation.strip() if self.english_translation else ""

    @property
    def cleaned_pronunciation(self) -> str | None:
        return self.pronunciation.strip() if self.pronunciation else None

    @property
    def cleaned_example_text(self) -> str | None:
        return self.example_text.strip() if self.example_text else None

    @property
    def cleaned_updated_by(self) -> str:
        return self.updated_by.strip() if self.updated_by else SYSTEM_UPDATED_BY


@dataclass(frozen=True)
class LearningItemDetails:
    item_id: int | None
    category_id: int
    category_name: str | None
    item_type: str
    source_text: str
    english_translation: str
    pronunciation: str | None
    example_text: str | None
    is_active: bool
    created_at: str | None
    updated_at: str | None
    updated_by: str | None

    @classmethod
    def from_domain(cls, learning_item: LearningItem):
        return cls(
            item_id=learning_item.item_id,
            category_id=learning_item.category_id,
            category_name=learning_item.category_name,
            item_type=learning_item.item_type,
            source_text=learning_item.source_text,
            english_translation=learning_item.english_translation,
            pronunciation=learning_item.pronunciation,
            example_text=learning_item.example_text,
            is_active=learning_item.is_active,
            created_at=learning_item.created_at,
            updated_at=learning_item.updated_at,
            updated_by=learning_item.updated_by,
        )

    def to_dict(self):
        return {
            "itemId": self.item_id,
            "categoryId": self.category_id,
            "categoryName": self.category_name,
            "itemType": self.item_type,
            "sourceText": self.source_text,
            "englishTranslation": self.english_translation,
            "pronunciation": self.pronunciation,
            "exampleText": self.example_text,
            "isActive": self.is_active,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "updatedBy": self.updated_by,
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())


LearningItemSummary = LearningItemDetails
