"""
Learning item API routes.

Responsibilities:
- Handle learning item CRUD route actions.
- Handle generated learning item example routes.
- Keep learning item endpoint logic out of app.py.
- Convert HTTP/JSON request data into learning item request contracts.
- Use mapper to convert request contracts into domain objects.
- Delegate domain-level CRUD use cases to LearningItemService.
- Convert returned domain objects into API-friendly response structures.
- Return consistent JSON API responses.

Architecture:
app.py -> route_registry -> learning_item_routes -> request contract
-> LearningItemMapper -> LearningItemService -> LearningItemValidator
-> LearningItemRepository -> SQLite
LearningItemService -> LearningItemExampleGenerator
"""

from src.api.route_utils import (
    extract_path_id,
    read_json_body,
    send_json,
)
from src.modules.lla.learning_items.learning_item_contracts import (
    CreateLearningItemRequest,
    UpdateLearningItemRequest,
)
from src.modules.lla.learning_items.learning_item_mapper import (
    LearningItemMapper,
)
from src.modules.lla.learning_items.learning_item_messages import (
    INVALID_JSON_BODY_MESSAGE,
    INVALID_LEARNING_ITEM_ID_MESSAGE,
    LEARNING_ITEM_CREATED_SUCCESS_MESSAGE,
    LEARNING_ITEM_DELETED_SUCCESS_MESSAGE,
    LEARNING_ITEM_NOT_FOUND_MESSAGE,
    LEARNING_ITEM_UPDATED_SUCCESS_MESSAGE,
)

learning_item_mapper = LearningItemMapper()


def handle_get_learning_items(handler, learning_item_service) -> None:
    learning_items = learning_item_service.get_all_learning_items()

    learning_item_responses = [
        learning_item_mapper.domain_to_details(learning_item).to_dict()
        for learning_item in learning_items
    ]

    send_json(
        handler,
        200,
        {
            "success": True,
            "learningItems": learning_item_responses,
        },
    )


def handle_get_learning_item_by_id(
    handler,
    learning_item_service,
    path: str,
) -> None:
    try:
        item_id = extract_path_id(path)
        learning_item_lookup = learning_item_mapper.item_id_to_domain(item_id)

        learning_item = learning_item_service.get_learning_item_by_id(
            learning_item_lookup
        )

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if learning_item is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": LEARNING_ITEM_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "learningItem": learning_item_mapper.domain_to_details(
                learning_item
            ).to_dict(),
        },
    )


def handle_generate_learning_item_examples(
    handler,
    learning_item_service,
    path: str,
) -> None:
    try:
        item_id = extract_path_id(path)

        learning_item_lookup = learning_item_mapper.item_id_to_domain(item_id)

        generated_examples = learning_item_service.generate_examples_for_learning_item(
            learning_item_lookup
        )

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "generatedExamples": [
                generated_example.to_dict() for generated_example in generated_examples
            ],
        },
    )


def handle_create_learning_item(handler, learning_item_service) -> None:
    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_JSON_BODY_MESSAGE,
            },
        )
        return

    try:
        create_request = CreateLearningItemRequest(
            category_id=int(request_data.get("categoryId", 0)),
            item_type=request_data.get("itemType", ""),
            source_text=request_data.get("sourceText", ""),
            english_translation=request_data.get("englishTranslation", ""),
            pronunciation=request_data.get("pronunciation"),
            example_text=request_data.get("exampleText"),
            is_active=bool(request_data.get("isActive", True)),
            updated_by=request_data.get("updatedBy"),
        )

        learning_item = learning_item_mapper.create_request_to_domain(create_request)

        created_item = learning_item_service.create_learning_item(learning_item)

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    send_json(
        handler,
        201,
        {
            "success": True,
            "message": LEARNING_ITEM_CREATED_SUCCESS_MESSAGE,
            "learningItem": learning_item_mapper.domain_to_details(
                created_item
            ).to_dict(),
        },
    )


def handle_update_learning_item(
    handler,
    learning_item_service,
    path: str,
) -> None:
    try:
        item_id = extract_path_id(path)

    except ValueError:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_LEARNING_ITEM_ID_MESSAGE,
            },
        )
        return

    request_data = read_json_body(handler)

    if request_data is None:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": INVALID_JSON_BODY_MESSAGE,
            },
        )
        return

    try:
        update_request = UpdateLearningItemRequest(
            item_id=item_id,
            category_id=int(request_data.get("categoryId", 0)),
            item_type=request_data.get("itemType", ""),
            source_text=request_data.get("sourceText", ""),
            english_translation=request_data.get("englishTranslation", ""),
            pronunciation=request_data.get("pronunciation"),
            example_text=request_data.get("exampleText"),
            is_active=bool(request_data.get("isActive", False)),
            updated_by=request_data.get("updatedBy"),
        )

        learning_item = learning_item_mapper.update_request_to_domain(update_request)

        updated_item = learning_item_service.update_learning_item(learning_item)

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if updated_item is None:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": LEARNING_ITEM_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": LEARNING_ITEM_UPDATED_SUCCESS_MESSAGE,
            "learningItem": learning_item_mapper.domain_to_details(
                updated_item
            ).to_dict(),
        },
    )


def handle_delete_learning_item(
    handler,
    learning_item_service,
    path: str,
) -> None:
    try:
        item_id = extract_path_id(path)
        learning_item = learning_item_mapper.item_id_to_domain(item_id)

        was_deleted = learning_item_service.delete_learning_item(learning_item)

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
        return

    if not was_deleted:
        send_json(
            handler,
            404,
            {
                "success": False,
                "error": LEARNING_ITEM_NOT_FOUND_MESSAGE,
            },
        )
        return

    send_json(
        handler,
        200,
        {
            "success": True,
            "message": LEARNING_ITEM_DELETED_SUCCESS_MESSAGE,
        },
    )
