"""
Workspace structure API routes.

Responsibilities:
- Handle workspace structure creation requests.
- Delegate validation and execution to WorkspaceStructureService.
- Keep HTTP transport logic separate from service logic.
"""

from src.api.route_utils import read_json_body, send_json
from src.core.automation.workspaces.workspace_structure_messages import (
    INVALID_JSON_BODY,
    WORKSPACE_STRUCTURE_CREATE_FAILED,
)


def handle_create_workspace_structure(handler, workspace_structure_service) -> None:
    try:
        request_data = read_json_body(handler)

        if request_data is None:
            send_json(
                handler,
                400,
                {
                    "success": False,
                    "errors": [INVALID_JSON_BODY],
                },
            )
            return

        result = workspace_structure_service.create_workspace_structure(
            request_data,
        )

        status_code = 200 if result.to_response()["success"] else 400

        send_json(
            handler,
            status_code,
            result.to_response(),
        )

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                "success": False,
                "errors": [str(error)],
            },
        )

    except Exception:
        send_json(
            handler,
            500,
            {
                "success": False,
                "errors": [WORKSPACE_STRUCTURE_CREATE_FAILED],
            },
        )
