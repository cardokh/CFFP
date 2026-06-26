"""
Shared API path constants.

Responsibilities:
- Centralize platform/core API route/path strings.
- Avoid hardcoded endpoint paths inside app.py and route modules.
- Support reusable route registration/dispatch infrastructure.

Architecture:
app.py -> api_paths
platform/core route modules -> api_paths
"""

API_PATH_HEALTH = "/api/health"
API_PATH_ECHO_PREFIX = "/api/echo"

API_PATH_AUTH_LOGIN = "/api/auth/login"
API_PATH_AUTH_REGISTER = "/api/auth/register"
API_PATH_AUTH_FORGOT_PASSWORD = "/api/auth/forgot-password"

API_PATH_ADMIN_USERS = "/api/admin/users"
API_PATH_ADMIN_USERS_PREFIX = "/api/admin/users/"

API_PATH_AI_SPEECH_GENERATE = "/api/ai/speech/generate"

API_PATH_CCORE_TASKS = "/api/ccore/tasks"
API_PATH_CCORE_TASKS_PREFIX = "/api/ccore/tasks/"
API_PATH_CCORE_TASK_STATUSES = "/api/ccore/task-statuses"
API_PATH_CCORE_EXECUTION_PROVIDERS = "/api/ccore/execution-providers"
API_PATH_CCORE_EXECUTION_IMPLEMENTER_TYPES = "/api/ccore/execution-implementer-types"
API_PATH_CCORE_EXECUTION_TARGETS = "/api/ccore/execution-targets"
API_PATH_CCORE_EXECUTION_CONFIGURATIONS = "/api/ccore/execution-configurations"

API_PATH_CCORE_METRICS = "/api/ccore/metrics"
API_PATH_CCORE_METRICS_PREFIX = "/api/ccore/metrics/"
API_PATH_CCORE_METRIC_TYPES = "/api/ccore/metric-types"

API_PATH_CCORE_PIPELINES = "/api/ccore/pipelines"
API_PATH_CCORE_PIPELINES_PREFIX = "/api/ccore/pipelines/"
API_PATH_CCORE_PIPELINE_STATUSES = "/api/ccore/pipeline-statuses"
