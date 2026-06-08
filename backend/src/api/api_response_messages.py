"""
Shared API response message constants.

Responsibilities:
- Centralize reusable infrastructure/API response messages.
- Avoid repeated hardcoded response text.
- Improve consistency across route handlers and dispatcher responses.

Architecture:
route handlers -> api_response_messages
app.py -> api_response_messages
"""

API_RESPONSE_STATUS_OK = "ok"

API_RESPONSE_MESSAGE_ECHO_WORKS = "echo works"

API_RESPONSE_ERROR_NOT_FOUND = "Not Found"

API_RESPONSE_ERROR_INVALID_JSON_BODY = "Invalid JSON body"
