"""
Local workspace filesystem adapter.

Responsibilities:
- Perform filesystem writes for workspace automation.
- Keep filesystem operations isolated from route handling and service orchestration.
"""

from pathlib import Path


class LocalWorkspaceFileSystem:
    """
    Adapter for local filesystem operations inside a controlled workspace root.
    """

    def create_folder(self, folder_path: Path) -> None:
        folder_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write_file(
        self,
        file_path: Path,
        content: str,
        overwrite: bool,
    ) -> bool:
        if file_path.exists() and not overwrite:
            return False

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path.write_text(
            content,
            encoding="utf-8",
        )

        return True
