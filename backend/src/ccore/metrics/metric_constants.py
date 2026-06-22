"""
CCore metric constants.

Responsibilities:
- Centralize metric table names, column names, default values, and API field names.
- Avoid duplicated literal values across repositories, services, routes, and mappers.
- Keep metric-specific constants inside the CCore metric boundary.
"""

CCORE_METRICS_TABLE_NAME = "ccore_metrics"
CCORE_METRIC_TYPES_TABLE_NAME = "ccore_metric_types"

CCORE_METRIC_ID_COLUMN = "metric_id"
CCORE_METRIC_NAME_COLUMN = "metric_name"
CCORE_METRIC_KEY_COLUMN = "metric_key"
CCORE_METRIC_TYPE_CODE_COLUMN = "metric_type_code"
CCORE_METRIC_CREATED_AT_COLUMN = "created_at"

CCORE_METRIC_TYPE_LABEL_COLUMN = "metric_type_label"
CCORE_METRIC_TYPE_SORT_ORDER_COLUMN = "sort_order"

CCORE_METRIC_DEFAULT_TYPE_CODE = "COUNTER"

CCORE_METRIC_API_FIELD_METRIC_ID = "metricId"
CCORE_METRIC_API_FIELD_METRIC_NAME = "metricName"
CCORE_METRIC_API_FIELD_METRIC_KEY = "metricKey"
CCORE_METRIC_API_FIELD_METRIC_TYPE = "metricType"
CCORE_METRIC_API_FIELD_METRIC_TYPE_LABEL = "metricTypeLabel"
CCORE_METRIC_API_FIELD_CREATED_AT = "createdAt"

CCORE_METRIC_TYPE_API_FIELD_CODE = "code"
CCORE_METRIC_TYPE_API_FIELD_LABEL = "label"
CCORE_METRIC_TYPE_API_FIELD_SORT_ORDER = "sortOrder"
