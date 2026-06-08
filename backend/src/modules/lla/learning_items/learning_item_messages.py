"""
Learning item messages.

Responsibilities:
- Centralize learning item validation and user-facing messages.
- Avoid hardcoded strings across validators, services, and routes.
- Prepare future localization/internationalization support.

Architecture:
Shared module constants/messages
"""

INVALID_LEARNING_ITEM_ID_MESSAGE = "Invalid learning item ID"

INVALID_CATEGORY_ID_MESSAGE = "Invalid category ID"

LEARNING_ITEM_TYPE_REQUIRED_MESSAGE = "Learning item type is required"

INVALID_LEARNING_ITEM_TYPE_MESSAGE = (
    "Learning item type must be one of: word, phrase, sentence"
)

SOURCE_TEXT_REQUIRED_MESSAGE = "Source text is required"

ENGLISH_TRANSLATION_REQUIRED_MESSAGE = "English translation is required"

DUPLICATE_LEARNING_ITEM_MESSAGE = "A learning item with this source text already exists"

LEARNING_ITEM_NOT_FOUND_MESSAGE = "Learning item not found"

LEARNING_ITEM_CREATED_SUCCESS_MESSAGE = "Learning item created successfully"

LEARNING_ITEM_UPDATED_SUCCESS_MESSAGE = "Learning item updated successfully"

LEARNING_ITEM_DELETED_SUCCESS_MESSAGE = "Learning item deleted successfully"

INVALID_JSON_BODY_MESSAGE = "Invalid JSON body"
