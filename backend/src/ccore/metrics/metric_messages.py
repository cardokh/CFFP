"""
CCore metric response and validation messages.

Responsibilities:
- Centralize metric-specific API and validation messages.
- Avoid duplicated user-facing/backend-facing message literals.
- Keep message wording consistent across routes, contracts, and validators.
"""

CCORE_METRIC_CREATED_SUCCESS_MESSAGE = "Metric created successfully."
CCORE_METRIC_UPDATED_SUCCESS_MESSAGE = "Metric updated successfully."
CCORE_METRIC_DELETED_SUCCESS_MESSAGE = "Metric deleted successfully."

CCORE_METRIC_NOT_FOUND_MESSAGE = "Metric not found."
CCORE_METRIC_INVALID_ID_MESSAGE = "A valid metric id is required."
CCORE_METRIC_INVALID_JSON_BODY_MESSAGE = "Invalid JSON body."
CCORE_METRIC_PAYLOAD_OBJECT_REQUIRED_MESSAGE = "Metric request payload must be a JSON object."
CCORE_METRIC_UNKNOWN_FIELD_MESSAGE = "Unsupported metric request field"

CCORE_METRIC_NAME_REQUIRED_MESSAGE = "Metric name is required."
CCORE_METRIC_KEY_REQUIRED_MESSAGE = "Metric key is required."
CCORE_METRIC_TYPE_REQUIRED_MESSAGE = "Metric type is required."
CCORE_METRIC_TYPE_INVALID_MESSAGE = "Metric type is invalid."
