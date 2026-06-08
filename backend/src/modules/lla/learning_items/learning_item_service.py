"""
Learning item application service.

Responsibilities:
- Coordinate learning item CRUD use cases.
- Keep API handlers separate from repository/database details.
- Delegate learning item validation to the learning item validator.
- Work with learning item domain objects only.
- Coordinate generated learning item examples through the example generator.

Architecture:
API -> Mapper -> LearningItemService -> LearningItemValidator -> LearningItemRepository -> SQLite Database
LearningItemService -> LearningItemExampleGenerator
"""

from src.modules.lla.learning_items.learning_item import LearningItem
from src.modules.lla.learning_items.learning_item_example_contracts import (
    LearningItemExampleResponse,
)


class LearningItemService:
    def __init__(
        self,
        learning_item_repository,
        learning_item_validator,
        learning_item_example_generator,
    ):
        self.learning_item_repository = learning_item_repository
        self.learning_item_validator = learning_item_validator
        self.learning_item_example_generator = learning_item_example_generator

    def get_all_learning_items(self) -> list[LearningItem]:
        return self.learning_item_repository.find_all_learning_items()

    def get_learning_item_by_id(
        self,
        learning_item: LearningItem,
    ) -> LearningItem | None:
        self.learning_item_validator.validate_learning_item_id(learning_item)

        return self.learning_item_repository.find_by_id(learning_item)

    def create_learning_item(
        self,
        learning_item: LearningItem,
    ) -> LearningItem:
        self.learning_item_validator.validate_create_learning_item(learning_item)

        return self.learning_item_repository.create_learning_item(learning_item)

    def update_learning_item(
        self,
        learning_item: LearningItem,
    ) -> LearningItem | None:
        self.learning_item_validator.validate_update_learning_item(learning_item)

        return self.learning_item_repository.update_learning_item(learning_item)

    def delete_learning_item(
        self,
        learning_item: LearningItem,
    ) -> bool:
        self.learning_item_validator.validate_learning_item_id(learning_item)

        return self.learning_item_repository.delete_learning_item(learning_item)

    def generate_examples_for_learning_item(
        self,
        learning_item: LearningItem,
    ) -> list[LearningItemExampleResponse]:
        self.learning_item_validator.validate_learning_item_id(learning_item)

        existing_learning_item = self.learning_item_repository.find_by_id(learning_item)

        if existing_learning_item is None:
            return []

        return self.learning_item_example_generator.generate_examples(
            existing_learning_item
        )
