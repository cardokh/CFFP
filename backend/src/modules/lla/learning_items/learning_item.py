"""
Learning item domain model.

Responsibilities:
- Represent one reusable linguistic learning unit.
- Store the category, type, source text, translation, pronunciation, and example text.
- Keep learning item data independent from lessons and quiz questions.

Architecture:
API -> Mapper -> Service -> Repository -> LearningItem
"""


class LearningItem:
    def __init__(
        self,
        item_id: int | None,
        category_id: int,
        item_type: str,
        source_text: str,
        english_translation: str,
        pronunciation: str | None,
        example_text: str | None,
        is_active: bool,
        category_name: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        updated_by: str | None = None,
    ):
        self.item_id = item_id
        self.category_id = category_id
        self.category_name = category_name
        self.item_type = item_type
        self.source_text = source_text
        self.english_translation = english_translation
        self.pronunciation = pronunciation
        self.example_text = example_text
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.updated_by = updated_by

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
