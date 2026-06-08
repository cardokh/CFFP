"""
Lesson learning item assignment domain model.

Represents an ordered assignment between a lesson and a learning item.
"""


class LessonLearningItemAssignment:
    def __init__(
        self,
        lesson_id: int,
        item_id: int,
        display_order: int,
        source_text: str | None = None,
        english_translation: str | None = None,
        pronunciation: str | None = None,
        example_text: str | None = None,
        item_type: str | None = None,
    ):
        self.lesson_id = lesson_id
        self.item_id = item_id
        self.display_order = display_order
        self.source_text = source_text
        self.english_translation = english_translation
        self.pronunciation = pronunciation
        self.example_text = example_text
        self.item_type = item_type
