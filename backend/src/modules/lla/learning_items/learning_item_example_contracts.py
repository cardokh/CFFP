"""
Learning item example contracts.

Responsibilities:
- Define structured response DTOs for generated learning item examples.
- Keep generated example response structures consistent.
- Separate generator/service data structures from raw API dictionaries.

Architecture:
LearningItemExampleGenerator
-> LearningItemExampleResponse
-> learning_item_routes
-> JSON API response
"""


class LearningItemExampleResponse:
    def __init__(
        self,
        source_text: str,
        english_translation: str,
        learning_focus: str,
        context: str,
        item_type: str,
    ):
        self.source_text = source_text
        self.english_translation = english_translation
        self.learning_focus = learning_focus
        self.context = context
        self.item_type = item_type

    def to_dict(self) -> dict:
        return {
            "sourceText": self.source_text,
            "englishTranslation": self.english_translation,
            "learningFocus": self.learning_focus,
            "context": self.context,
            "itemType": self.item_type,
        }
