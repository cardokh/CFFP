"""
Workspace structure request validation.

Responsibilities:
- Validate the transport request before the service performs filesystem work.
- Keep route handlers thin.
- Enforce basic contract shape and safe relative path rules.
"""

from pathlib import Path

from src.core.automation.workspaces.workspace_structure_contracts import (
    WORKSPACE_STRUCTURE_REQUEST_BASE_PATH,
    WORKSPACE_STRUCTURE_REQUEST_FILES,
    WORKSPACE_STRUCTURE_REQUEST_FILE_CONTENT,
    WORKSPACE_STRUCTURE_REQUEST_FILE_PATH,
    WORKSPACE_STRUCTURE_REQUEST_FOLDERS,
    WORKSPACE_STRUCTURE_REQUEST_OVERWRITE_FILES,
)
from src.core.automation.workspaces.workspace_structure_messages import (
    ABSOLUTE_PATH_NOT_ALLOWED,
    BASE_PATH_REQUIRED,
    FILES_MUST_BE_LIST,
    FILE_CONTENT_MUST_BE_STRING,
    FILE_ENTRY_MUST_BE_OBJECT,
    FILE_PATH_MUST_BE_STRING,
    FOLDERS_MUST_BE_LIST,
    FOLDER_PATH_MUST_BE_STRING,
    OVERWRITE_FILES_MUST_BE_BOOLEAN,
    PARENT_TRAVERSAL_NOT_ALLOWED,
)


class WorkspaceStructureValidator:
    """
    Validates workspace structure creation requests.
    """

    def validate(self, request_data: dict) -> None:
        base_path = request_data.get(WORKSPACE_STRUCTURE_REQUEST_BASE_PATH)
        folders = request_data.get(WORKSPACE_STRUCTURE_REQUEST_FOLDERS, [])
        files = request_data.get(WORKSPACE_STRUCTURE_REQUEST_FILES, [])
        overwrite_files = request_data.get(
            WORKSPACE_STRUCTURE_REQUEST_OVERWRITE_FILES,
            False,
        )

        if not isinstance(base_path, str) or not base_path.strip():
            raise ValueError(BASE_PATH_REQUIRED)

        self._validate_relative_path(base_path)

        if not isinstance(folders, list):
            raise ValueError(FOLDERS_MUST_BE_LIST)

        if not isinstance(files, list):
            raise ValueError(FILES_MUST_BE_LIST)

        if not isinstance(overwrite_files, bool):
            raise ValueError(OVERWRITE_FILES_MUST_BE_BOOLEAN)

        for folder_path in folders:
            if not isinstance(folder_path, str) or not folder_path.strip():
                raise ValueError(FOLDER_PATH_MUST_BE_STRING)

            self._validate_relative_path(folder_path)

        for file_entry in files:
            if not isinstance(file_entry, dict):
                raise ValueError(FILE_ENTRY_MUST_BE_OBJECT)

            file_path = file_entry.get(WORKSPACE_STRUCTURE_REQUEST_FILE_PATH)
            content = file_entry.get(WORKSPACE_STRUCTURE_REQUEST_FILE_CONTENT)

            if not isinstance(file_path, str) or not file_path.strip():
                raise ValueError(FILE_PATH_MUST_BE_STRING)

            if not isinstance(content, str):
                raise ValueError(FILE_CONTENT_MUST_BE_STRING)

            self._validate_relative_path(file_path)

    def _validate_relative_path(self, value: str) -> None:
        candidate_path = Path(value)

        if candidate_path.is_absolute():
            raise ValueError(ABSOLUTE_PATH_NOT_ALLOWED)

        if any(path_part == ".." for path_part in candidate_path.parts):
            raise ValueError(PARENT_TRAVERSAL_NOT_ALLOWED)
