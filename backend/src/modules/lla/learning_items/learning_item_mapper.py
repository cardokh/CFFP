"""
Learning item mapper.

Responsibilities:
- Convert learning item request contracts into domain objects.
- Convert learning item domain objects into response contracts.
- Centralize mapping logic between architectural layers.

Architecture:
Contracts <-> Mapper <-> Domain
"""

from src.modules.lla.learning_items.learning_item import LearningItem
from src.modules.lla.learning_items.learning_item_contracts import (
    CreateLearningItemRequest,
    LearningItemDetails,
    UpdateLearningItemRequest,
)


class LearningItemMapper:
    @staticmethod
    def create_request_to_domain(
        request: CreateLearningItemRequest,
    ) -> LearningItem:
        return LearningItem(
            item_id=None,
            category_id=request.category_id,
            item_type=request.cleaned_item_type,
            source_text=request.cleaned_source_text,
            english_translation=request.cleaned_english_translation,
            pronunciation=request.cleaned_pronunciation,
            example_text=request.cleaned_example_text,
            is_active=request.is_active,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def update_request_to_domain(
        request: UpdateLearningItemRequest,
    ) -> LearningItem:
        return LearningItem(
            item_id=request.item_id,
            category_id=request.category_id,
            item_type=request.cleaned_item_type,
            source_text=request.cleaned_source_text,
            english_translation=request.cleaned_english_translation,
            pronunciation=request.cleaned_pronunciation,
            example_text=request.cleaned_example_text,
            is_active=request.is_active,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def item_id_to_domain(item_id: int) -> LearningItem:
        return LearningItem(
            item_id=item_id,
            category_id=0,
            item_type="",
            source_text="",
            english_translation="",
            pronunciation=None,
            example_text=None,
            is_active=True,
        )

    @staticmethod
    def source_text_to_domain(source_text: str) -> LearningItem:
        return LearningItem(
            item_id=None,
            category_id=0,
            item_type="",
            source_text=source_text,
            english_translation="",
            pronunciation=None,
            example_text=None,
            is_active=True,
        )

    @staticmethod
    def domain_to_details(
        learning_item: LearningItem,
    ) -> LearningItemDetails:
        return LearningItemDetails.from_domain(learning_item)
