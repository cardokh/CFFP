"""
Reference data API routes.

Responsibilities:
- Handle read-only reference-data endpoints.
- Keep reference-data routing separate from app.py.
- Delegate business logic to ReferenceDataService.
- Return API-friendly JSON responses.

Architecture:
app.py -> route_registry -> reference_data_routes -> ReferenceDataService -> Repository/SQLite
"""

from src.api.route_utils import send_json


def handle_get_lesson_form_options(handler, reference_data_service) -> None:
    form_options = reference_data_service.get_lesson_form_options()

    send_json(
        handler,
        200,
        {
            "success": True,
            "form_options": form_options,
        },
    )
