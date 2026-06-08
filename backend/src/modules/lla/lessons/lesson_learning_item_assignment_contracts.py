"""
Lesson learning item assignment contracts.

Responsibilities:
- Define request and response structures for lesson learning item assignments.
- Centralize API-friendly response serialization.
"""

from dataclasses import dataclass

from src.api.contract_utils import dict_keys_to_camel_case
from src.modules.lla.lessons.lesson_learning_item_assignment import (
    LessonLearningItemAssignment,
)


@dataclass(frozen=True)
class LessonLearningItemAssignmentRequest:
    lesson_id: int
    item_id: int
    display_order: int


@dataclass(frozen=True)
class LessonLearningItemAssignmentDetails:
    lesson_id: int
    item_id: int
    display_order: int
    source_text: str | None = None
    english_translation: str | None = None
    pronunciation: str | None = None
    example_text: str | None = None
    item_type: str | None = None

    @classmethod
    def from_domain(
        cls,
        assignment: LessonLearningItemAssignment,
    ):
        return cls(
            lesson_id=assignment.lesson_id,
            item_id=assignment.item_id,
            display_order=assignment.display_order,
            source_text=assignment.source_text,
            english_translation=assignment.english_translation,
            pronunciation=assignment.pronunciation,
            example_text=assignment.example_text,
            item_type=assignment.item_type,
        )

    def to_dict(self):
        return {
            "lesson_id": self.lesson_id,
            "item_id": self.item_id,
            "display_order": self.display_order,
            "source_text": self.source_text,
            "english_translation": self.english_translation,
            "pronunciation": self.pronunciation,
            "example_text": self.example_text,
            "item_type": self.item_type,
        }

    def to_camel_dict(self):
        return dict_keys_to_camel_case(self.to_dict())
