"""
Learning item example generator.

Responsibilities:
- Generate additional contextual examples for a learning item.
- Keep example generation logic isolated from the learning item service.
- Provide a replaceable boundary for future AI-based example generation.

Architecture:
LearningItemService -> LearningItemExampleGenerator

Note:
This first implementation is deterministic and template-based.
It does not perform real translation. A future AI-backed implementation
can replace this class without changing the service layer.
"""

from src.modules.lla.learning_items.learning_item import LearningItem
from src.modules.lla.learning_items.learning_item_example_contracts import (
    LearningItemExampleResponse,
)


class LearningItemExampleGenerator:
    def generate_examples(
        self,
        learning_item: LearningItem,
    ) -> list[LearningItemExampleResponse]:
        source_text = self._clean_text(learning_item.source_text)

        english_translation = self._clean_text(learning_item.english_translation)

        category_name = self._clean_text(learning_item.category_name)

        item_type = self._clean_text(learning_item.item_type)

        return [
            LearningItemExampleResponse(
                source_text=f"Kan jag få {source_text.lower()}?",
                english_translation=f"Can I have {english_translation.lower()}?",
                learning_focus="Request",
                context=category_name,
                item_type=item_type,
            ),
            LearningItemExampleResponse(
                source_text=f"Jag skulle vilja ha {source_text.lower()}.",
                english_translation=f"I would like {english_translation.lower()}.",
                learning_focus="Polite",
                context=category_name,
                item_type=item_type,
            ),
            LearningItemExampleResponse(
                source_text=f"Har ni {source_text.lower()}?",
                english_translation=f"Do you have {english_translation.lower()}?",
                learning_focus="Question",
                context=category_name,
                item_type=item_type,
            ),
        ]

    def _clean_text(
        self,
        value: str | None,
    ) -> str:
        cleaned_value = str(value or "").strip()

        if cleaned_value:
            return cleaned_value

        return "—"
