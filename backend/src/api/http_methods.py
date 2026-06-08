"""
HTTP method constants.

Responsibilities:
- Centralize HTTP method names used by the API dispatcher and route registries.
- Avoid repeated hardcoded method strings.
- Keep route registration and request dispatch consistent.

Architecture:
app.py -> http_methods
route registries -> http_methods
route dispatcher -> method-keyed route dictionaries
"""

HTTP_METHOD_GET = "GET"
HTTP_METHOD_POST = "POST"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_DELETE = "DELETE"
