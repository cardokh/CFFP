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
