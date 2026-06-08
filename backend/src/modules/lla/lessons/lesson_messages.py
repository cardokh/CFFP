"""
Lesson messages.

Responsibilities:
- Centralize lesson validation and user-facing messages.
- Avoid hardcoded strings across validators, services, and routes.
- Prepare future localization/internationalization support.

Architecture:
Shared module constants/messages
"""

INVALID_LESSON_ID_MESSAGE = "Invalid lesson ID"

INVALID_CATEGORY_ID_MESSAGE = "Invalid category ID"

INVALID_LESSON_TYPE_ID_MESSAGE = "Invalid lesson type ID"

INVALID_EMBODIMENT_TYPE_ID_MESSAGE = "Invalid embodiment type ID"

INVALID_INTERACTION_STYLE_ID_MESSAGE = "Invalid interaction style ID"

LESSON_TITLE_REQUIRED_MESSAGE = "Lesson title is required"

LESSON_NOT_FOUND_MESSAGE = "Lesson not found"

LESSON_CREATED_SUCCESS_MESSAGE = "Lesson created successfully"

LESSON_UPDATED_SUCCESS_MESSAGE = "Lesson updated successfully"

LESSON_DELETED_SUCCESS_MESSAGE = "Lesson deleted successfully"

INVALID_JSON_BODY_MESSAGE = "Invalid JSON body"
