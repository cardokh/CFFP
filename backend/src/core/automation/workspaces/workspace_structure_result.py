"""
Workspace structure execution result.
"""

from src.core.automation.workspaces.workspace_structure_contracts import (
    WORKSPACE_STRUCTURE_RESPONSE_CREATED_FILES,
    WORKSPACE_STRUCTURE_RESPONSE_CREATED_FILE_PATHS,
    WORKSPACE_STRUCTURE_RESPONSE_CREATED_FOLDERS,
    WORKSPACE_STRUCTURE_RESPONSE_CREATED_FOLDER_PATHS,
    WORKSPACE_STRUCTURE_RESPONSE_ERRORS,
    WORKSPACE_STRUCTURE_RESPONSE_SKIPPED_FILES,
    WORKSPACE_STRUCTURE_RESPONSE_SKIPPED_FILE_PATHS,
    WORKSPACE_STRUCTURE_RESPONSE_SUCCESS,
)


class WorkspaceStructureResult:
    """
    Mutable execution result for workspace structure creation.
    """

    def __init__(self):
        self.created_folder_paths = []
        self.created_file_paths = []
        self.skipped_file_paths = []
        self.errors = []

    def add_created_folder(self, path: str) -> None:
        self.created_folder_paths.append(path)

    def add_created_file(self, path: str) -> None:
        self.created_file_paths.append(path)

    def add_skipped_file(self, path: str) -> None:
        self.skipped_file_paths.append(path)

    def add_error(self, path: str, message: str) -> None:
        self.errors.append(
            {
                "path": path,
                "message": message,
            }
        )

    def to_response(self) -> dict:
        return {
            WORKSPACE_STRUCTURE_RESPONSE_SUCCESS: not self.errors,
            WORKSPACE_STRUCTURE_RESPONSE_CREATED_FOLDERS: len(
                self.created_folder_paths,
            ),
            WORKSPACE_STRUCTURE_RESPONSE_CREATED_FILES: len(
                self.created_file_paths,
            ),
            WORKSPACE_STRUCTURE_RESPONSE_SKIPPED_FILES: len(
                self.skipped_file_paths,
            ),
            WORKSPACE_STRUCTURE_RESPONSE_ERRORS: self.errors,
            WORKSPACE_STRUCTURE_RESPONSE_CREATED_FOLDER_PATHS: self.created_folder_paths,
            WORKSPACE_STRUCTURE_RESPONSE_CREATED_FILE_PATHS: self.created_file_paths,
            WORKSPACE_STRUCTURE_RESPONSE_SKIPPED_FILE_PATHS: self.skipped_file_paths,
        }
