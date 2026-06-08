"""
Quiz question messages.

Responsibilities:
- Centralize quiz question validation and user-facing messages.
- Avoid hardcoded strings across validators, services, and routes.
- Prepare future localization/internationalization support.

Architecture:
Shared module constants/messages
"""

INVALID_QUIZ_QUESTION_ID_MESSAGE = "Invalid quiz question ID"

INVALID_CATEGORY_ID_MESSAGE = "Invalid category ID"

QUESTION_TEXT_REQUIRED_MESSAGE = "Question text is required"

DUPLICATE_QUIZ_QUESTION_MESSAGE = (
    "A quiz question with this question text already exists"
)

QUIZ_QUESTION_NOT_FOUND_MESSAGE = "Quiz question not found"

QUIZ_QUESTION_CREATED_SUCCESS_MESSAGE = "Quiz question created successfully"

QUIZ_QUESTION_UPDATED_SUCCESS_MESSAGE = "Quiz question updated successfully"

QUIZ_QUESTION_DELETED_SUCCESS_MESSAGE = "Quiz question deleted successfully"

INVALID_JSON_BODY_MESSAGE = "Invalid JSON body"
