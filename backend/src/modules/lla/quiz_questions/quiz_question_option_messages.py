"""
Quiz question option messages.

Responsibilities:
- Centralize quiz question option validation and user-facing messages.
- Avoid hardcoded strings across validators, services, and routes.
- Prepare future localization/internationalization support.

Architecture:
Shared module constants/messages
"""

INVALID_QUIZ_QUESTION_OPTION_ID_MESSAGE = "Invalid quiz question option ID"

INVALID_QUIZ_QUESTION_ID_MESSAGE = "Invalid quiz question ID"

OPTION_TEXT_REQUIRED_MESSAGE = "Answer option text is required"

INVALID_DISPLAY_ORDER_MESSAGE = "Display order must be greater than zero"

MINIMUM_ANSWER_OPTIONS_REQUIRED_MESSAGE = (
    "A quiz question must have at least two answer options"
)

EXACTLY_ONE_CORRECT_ANSWER_REQUIRED_MESSAGE = (
    "A quiz question must have exactly one correct answer"
)

INVALID_ANSWER_OPTION_ORDER_MESSAGE = "Answer option display order is invalid"

QUIZ_QUESTION_OPTION_NOT_FOUND_MESSAGE = "Quiz question option not found"

QUIZ_QUESTION_OPTION_CREATED_SUCCESS_MESSAGE = (
    "Quiz question option created successfully"
)

QUIZ_QUESTION_OPTION_UPDATED_SUCCESS_MESSAGE = (
    "Quiz question option updated successfully"
)

QUIZ_QUESTION_OPTION_DELETED_SUCCESS_MESSAGE = (
    "Quiz question option deleted successfully"
)

QUIZ_QUESTION_OPTIONS_UPDATED_SUCCESS_MESSAGE = (
    "Quiz question options updated successfully"
)

INVALID_JSON_BODY_MESSAGE = "Invalid JSON body"
