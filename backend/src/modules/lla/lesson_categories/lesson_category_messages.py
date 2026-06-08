"""
Lesson category messages.

Responsibilities:
- Centralize lesson category validation and user-facing messages.
- Avoid hardcoded strings across validators, services, and routes.
- Prepare future localization/internationalization support.

Architecture:
Shared module constants/messages
"""

INVALID_CATEGORY_ID_MESSAGE = "Invalid category ID"

CATEGORY_NAME_REQUIRED_MESSAGE = "Category name is required"

DUPLICATE_CATEGORY_NAME_MESSAGE = "A lesson category with this name already exists"

LESSON_CATEGORY_NOT_FOUND_MESSAGE = "Lesson category not found"

LESSON_CATEGORY_CREATED_SUCCESS_MESSAGE = "Lesson category created successfully"

LESSON_CATEGORY_UPDATED_SUCCESS_MESSAGE = "Lesson category updated successfully"

LESSON_CATEGORY_DELETED_SUCCESS_MESSAGE = "Lesson category deleted successfully"

INVALID_JSON_BODY_MESSAGE = "Invalid JSON body"
