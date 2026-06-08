"""
Learning item validation.

Responsibilities:
- Validate learning item business rules.
- Keep validation concerns separate from service orchestration.
- Validate learning item domain objects only.

Architecture:
Service -> Validator -> Repository
"""

from src.modules.lla.learning_items.learning_item import LearningItem
from src.modules.lla.learning_items.learning_item_messages import (
    DUPLICATE_LEARNING_ITEM_MESSAGE,
    ENGLISH_TRANSLATION_REQUIRED_MESSAGE,
    INVALID_CATEGORY_ID_MESSAGE,
    INVALID_LEARNING_ITEM_ID_MESSAGE,
    INVALID_LEARNING_ITEM_TYPE_MESSAGE,
    LEARNING_ITEM_TYPE_REQUIRED_MESSAGE,
    SOURCE_TEXT_REQUIRED_MESSAGE,
)

ALLOWED_LEARNING_ITEM_TYPES = {
    "word",
    "phrase",
    "sentence",
}


class LearningItemValidator:
    def __init__(self, learning_item_repository):
        self.learning_item_repository = learning_item_repository

    def validate_create_learning_item(
        self,
        learning_item: LearningItem,
    ):
        self._validate_learning_item_fields(learning_item)

        existing_item = self.learning_item_repository.find_by_source_text(learning_item)

        if existing_item is not None:
            raise ValueError(DUPLICATE_LEARNING_ITEM_MESSAGE)

    def validate_update_learning_item(
        self,
        learning_item: LearningItem,
    ):
        self.validate_learning_item_id(learning_item)

        self._validate_learning_item_fields(learning_item)

        existing_item_with_source_text = (
            self.learning_item_repository.find_by_source_text(learning_item)
        )

        if (
            existing_item_with_source_text is not None
            and existing_item_with_source_text.item_id != learning_item.item_id
        ):
            raise ValueError(DUPLICATE_LEARNING_ITEM_MESSAGE)

    @staticmethod
    def validate_learning_item_id(learning_item: LearningItem):
        if learning_item.item_id is None or learning_item.item_id <= 0:
            raise ValueError(INVALID_LEARNING_ITEM_ID_MESSAGE)

    @staticmethod
    def _validate_learning_item_fields(
        learning_item: LearningItem,
    ):
        if learning_item.category_id is None or learning_item.category_id <= 0:
            raise ValueError(INVALID_CATEGORY_ID_MESSAGE)

        if not learning_item.item_type:
            raise ValueError(LEARNING_ITEM_TYPE_REQUIRED_MESSAGE)

        normalized_item_type = learning_item.item_type.strip().lower()

        if normalized_item_type not in ALLOWED_LEARNING_ITEM_TYPES:
            raise ValueError(INVALID_LEARNING_ITEM_TYPE_MESSAGE)

        if not learning_item.source_text:
            raise ValueError(SOURCE_TEXT_REQUIRED_MESSAGE)

        if not learning_item.english_translation:
            raise ValueError(ENGLISH_TRANSLATION_REQUIRED_MESSAGE)
