"""
Shared API constants.

Responsibilities:
- Centralize API-level constants.
- Avoid hardcoded HTTP headers, content types, encodings, and CORS values.
- Support reusable route utilities and future route delegate modules.

Architecture:
API route modules -> api_constants
API route utilities -> api_constants
app.py -> API route utilities/constants
"""

API_SERVER_HOST = "127.0.0.1"
API_SERVER_PORT = 8000
API_SERVER_BASE_URL = f"http://{API_SERVER_HOST}:{API_SERVER_PORT}"

ALLOWED_CORS_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

HTTP_HEADER_ORIGIN = "Origin"
HTTP_HEADER_CONTENT_TYPE = "Content-Type"
HTTP_HEADER_CONTENT_LENGTH = "Content-Length"

HTTP_HEADER_ACCESS_CONTROL_ALLOW_ORIGIN = "Access-Control-Allow-Origin"
HTTP_HEADER_ACCESS_CONTROL_ALLOW_METHODS = "Access-Control-Allow-Methods"
HTTP_HEADER_ACCESS_CONTROL_ALLOW_HEADERS = "Access-Control-Allow-Headers"

HTTP_ALLOWED_METHODS = "GET, POST, PUT, DELETE, OPTIONS"

CONTENT_TYPE_JSON_UTF8 = "application/json; charset=utf-8"

TEXT_ENCODING_UTF8 = "utf-8"

DEFAULT_CONTENT_LENGTH = "0"

PATH_SEPARATOR = "/"

CONTENT_TYPE_AUDIO_MPEG = "audio/mpeg"

TTS_SWEDISH_LANGUAGE_CODE = "sv"
TTS_OUTPUT_FILENAME = "tts.mp3"
