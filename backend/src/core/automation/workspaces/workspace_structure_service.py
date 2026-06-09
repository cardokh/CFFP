"""
Workspace structure service.

Responsibilities:
- Create folders and files within the configured workspace root.
- Enforce workspace root restrictions.
- Return an execution result suitable for API responses and future automation logs.
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
    PATH_ESCAPES_WORKSPACE_ROOT,
)
from src.core.automation.workspaces.workspace_structure_result import (
    WorkspaceStructureResult,
)


class WorkspaceStructureService:
    """
    Creates workspace folder and file structures under a controlled root.
    """

    def __init__(
        self,
        workspace_root: Path,
        workspace_file_system,
        workspace_structure_validator,
    ):
        self._workspace_root = workspace_root.resolve()
        self._workspace_file_system = workspace_file_system
        self._workspace_structure_validator = workspace_structure_validator

    def create_workspace_structure(self, request_data: dict) -> WorkspaceStructureResult:
        self._workspace_structure_validator.validate(request_data)

        result = WorkspaceStructureResult()
        base_path = request_data[WORKSPACE_STRUCTURE_REQUEST_BASE_PATH]
        folders = request_data.get(WORKSPACE_STRUCTURE_REQUEST_FOLDERS, [])
        files = request_data.get(WORKSPACE_STRUCTURE_REQUEST_FILES, [])
        overwrite_files = request_data.get(
            WORKSPACE_STRUCTURE_REQUEST_OVERWRITE_FILES,
            False,
        )

        base_target_path = self._resolve_workspace_path(base_path)
        self._workspace_file_system.create_folder(base_target_path)

        for folder_path in folders:
            target_folder_path = self._resolve_workspace_path(
                base_path,
                folder_path,
            )

            self._workspace_file_system.create_folder(target_folder_path)
            result.add_created_folder(
                self._to_workspace_relative_path(target_folder_path),
            )

        for file_entry in files:
            file_path = file_entry[WORKSPACE_STRUCTURE_REQUEST_FILE_PATH]
            content = file_entry[WORKSPACE_STRUCTURE_REQUEST_FILE_CONTENT]
            target_file_path = self._resolve_workspace_path(
                base_path,
                file_path,
            )

            was_created = self._workspace_file_system.write_file(
                target_file_path,
                content,
                overwrite_files,
            )

            if was_created:
                result.add_created_file(
                    self._to_workspace_relative_path(target_file_path),
                )
            else:
                result.add_skipped_file(
                    self._to_workspace_relative_path(target_file_path),
                )

        return result

    def _resolve_workspace_path(self, *path_parts: str) -> Path:
        target_path = self._workspace_root.joinpath(*path_parts).resolve()

        try:
            target_path.relative_to(self._workspace_root)
        except ValueError as error:
            raise ValueError(PATH_ESCAPES_WORKSPACE_ROOT) from error

        return target_path

    def _to_workspace_relative_path(self, target_path: Path) -> str:
        return target_path.relative_to(self._workspace_root).as_posix()
