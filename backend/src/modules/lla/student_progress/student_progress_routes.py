"""
Student progress API routes.

Responsibilities:
- Handle student progress HTTP requests.
- Delegate progress retrieval to the service layer.
- Convert domain objects into API response contracts.
- Return consistent JSON API responses.

Architecture:
HTTP -> Routes -> Service -> Repository -> Domain -> Mapper -> Contracts -> JSON
"""

from src.api.route_utils import (
    extract_path_id,
    send_json,
)
from src.modules.lla.student_progress.student_progress_mapper import (
    StudentProgressMapper,
)
from src.modules.lla.student_progress.student_progress_messages import (
    STUDENT_PROGRESS_FETCHED_SUCCESSFULLY,
)

student_progress_mapper = StudentProgressMapper()


def handle_get_student_progress(
    handler,
    student_progress_service,
    path,
):
    try:
        user_id = extract_path_id(path)

        overview = student_progress_service.get_student_progress_overview(
            user_id,
        )

        progress_response = student_progress_mapper.domain_to_details(
            overview,
        ).to_camel_dict()

        send_json(
            handler,
            200,
            {
                "success": True,
                "message": STUDENT_PROGRESS_FETCHED_SUCCESSFULLY,
                "progress": progress_response,
            },
        )

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "error": str(error),
            },
        )
