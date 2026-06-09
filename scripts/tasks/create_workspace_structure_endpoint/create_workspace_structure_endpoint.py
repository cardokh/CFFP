import sys
from pathlib import Path
from typing import Any


def _configure_project_import_path() -> None:
    current_path = Path(__file__).resolve()

    for parent_path in current_path.parents:
        candidate_path = parent_path / "scripts" / "shared" / "base_script.py"

        if candidate_path.exists():
            project_root = str(parent_path)

            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            return

    raise RuntimeError("Unable to locate project root for script imports.")


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_file_utils import ensure_parent_folder
from scripts.shared.script_json_utils import read_json_file, write_json_file


class CreateWorkspaceStructureEndpointScript(BaseScript):
    """
    Generates the WA-1 workspace structure endpoint from configuration.

    The script is intentionally generic. It reads configured folders, files,
    text replacements, and JSON merges, then writes a structured execution
    report through the shared BaseScript output mechanism.
    """

    def __init__(self):
        super().__init__(__file__)
        self.created_folders = []
        self.created_files = []
        self.updated_files = []
        self.skipped_files = []
        self.applied_replacements = []
        self.updated_json_files = []
        self.errors = []

    def run(self) -> None:
        self._create_folders()
        self._write_files()
        self._apply_text_replacements()
        self._merge_json_files()

        report = self._build_report()
        report_path = self.write_json_report(report)

        if self.errors:
            print_failed(
                "Workspace structure endpoint generation failed. "
                f"Report: {self.to_project_relative_path(report_path)}"
            )
            raise SystemExit(1)

        print_passed(
            "Workspace structure endpoint generated. "
            f"Report: {self.to_project_relative_path(report_path)}"
        )

    def _create_folders(self) -> None:
        for folder_entry in self._get_config_list("folders"):
            relative_path = self._get_required_string(
                folder_entry,
                "path",
                "Folder entry must contain a non-empty path.",
            )

            target_path = self._resolve_project_path(relative_path)
            target_path.mkdir(parents=True, exist_ok=True)
            self.created_folders.append(self.to_project_relative_path(target_path))

    def _write_files(self) -> None:
        for file_entry in self._get_config_list("files"):
            relative_path = self._get_required_string(
                file_entry,
                "path",
                "File entry must contain a non-empty path.",
            )

            if "content" not in file_entry or not isinstance(
                file_entry["content"], str
            ):
                raise ValueError("File entry must contain string content.")

            overwrite = self._get_optional_bool(file_entry, "overwrite", False)
            target_path = self._resolve_project_path(relative_path)

            if target_path.exists() and not overwrite:
                self.skipped_files.append(self.to_project_relative_path(target_path))
                continue

            ensure_parent_folder(target_path)
            target_path.write_text(file_entry["content"], encoding="utf-8")
            self.created_files.append(self.to_project_relative_path(target_path))

    def _apply_text_replacements(self) -> None:
        for replacement_entry in self._get_config_list("textReplacements"):
            relative_path = self._get_required_string(
                replacement_entry,
                "path",
                "Text replacement entry must contain a non-empty path.",
            )
            old_text = self._get_required_string(
                replacement_entry,
                "oldText",
                "Text replacement entry must contain non-empty oldText.",
            )
            new_text = self._get_required_string(
                replacement_entry,
                "newText",
                "Text replacement entry must contain non-empty newText.",
            )
            required = self._get_optional_bool(replacement_entry, "required", True)
            target_path = self._resolve_project_path(relative_path)

            if not target_path.exists():
                self._record_error(
                    "TEXT_REPLACEMENT_TARGET_MISSING",
                    target_path,
                    "Text replacement target file does not exist.",
                )
                continue

            content = target_path.read_text(encoding="utf-8")

            if new_text in content:
                self._record_replacement(target_path, "alreadyApplied")
                continue

            if old_text not in content:
                if required:
                    self._record_error(
                        "TEXT_REPLACEMENT_PATTERN_MISSING",
                        target_path,
                        "Required text replacement pattern was not found.",
                    )
                continue

            target_path.write_text(
                content.replace(old_text, new_text, 1), encoding="utf-8"
            )
            self.updated_files.append(self.to_project_relative_path(target_path))
            self._record_replacement(target_path, "applied")

    def _merge_json_files(self) -> None:
        for json_entry in self._get_config_list("jsonMerges"):
            relative_path = self._get_required_string(
                json_entry,
                "path",
                "JSON merge entry must contain a non-empty path.",
            )

            values = json_entry.get("values")

            if not isinstance(values, dict):
                raise ValueError("JSON merge entry must contain object values.")

            target_path = self._resolve_project_path(relative_path)
            data = read_json_file(target_path) if target_path.exists() else {}
            data.update(values)
            write_json_file(target_path, data)
            self.updated_json_files.append(self.to_project_relative_path(target_path))

    def _get_config_list(self, key: str) -> list[dict[str, Any]]:
        values = self.config.get(key, [])

        if not isinstance(values, list):
            raise ValueError(f"Config value must be a list: {key}")

        for value in values:
            if not isinstance(value, dict):
                raise ValueError(f"Config list must contain objects only: {key}")

        return values

    def _get_required_string(
        self,
        data: dict[str, Any],
        key: str,
        error_message: str,
    ) -> str:
        value = data.get(key)

        if not isinstance(value, str) or not value:
            raise ValueError(error_message)

        return value

    def _get_optional_bool(
        self,
        data: dict[str, Any],
        key: str,
        default_value: bool,
    ) -> bool:
        value = data.get(key, default_value)

        if not isinstance(value, bool):
            raise ValueError(f"Config value must be boolean: {key}")

        return value

    def _resolve_project_path(self, relative_path: str) -> Path:
        candidate_path = Path(relative_path)

        if candidate_path.is_absolute():
            raise ValueError(f"Absolute paths are not allowed: {relative_path}")

        if any(path_part == ".." for path_part in candidate_path.parts):
            raise ValueError(f"Parent traversal is not allowed: {relative_path}")

        project_root = self.project_root.resolve()
        target_path = (project_root / candidate_path).resolve()

        try:
            target_path.relative_to(project_root)
        except ValueError as error:
            raise ValueError(f"Path escapes project root: {relative_path}") from error

        return target_path

    def _record_replacement(self, target_path: Path, status: str) -> None:
        self.applied_replacements.append(
            {
                "path": self.to_project_relative_path(target_path),
                "status": status,
            }
        )

    def _record_error(self, error_code: str, target_path: Path, message: str) -> None:
        self.errors.append(
            {
                "errorCode": error_code,
                "path": self.to_project_relative_path(target_path),
                "message": message,
            }
        )

    def _build_report(self) -> dict[str, Any]:
        return {
            "scriptName": self.script_name,
            "status": "FAILED" if self.errors else "PASSED",
            "summary": {
                "createdFolderCount": len(self.created_folders),
                "createdFileCount": len(self.created_files),
                "updatedFileCount": len(set(self.updated_files)),
                "skippedFileCount": len(self.skipped_files),
                "appliedReplacementCount": len(self.applied_replacements),
                "updatedJsonFileCount": len(self.updated_json_files),
                "errorCount": len(self.errors),
            },
            "createdFolders": self.created_folders,
            "createdFiles": self.created_files,
            "updatedFiles": sorted(set(self.updated_files)),
            "skippedFiles": self.skipped_files,
            "appliedReplacements": self.applied_replacements,
            "updatedJsonFiles": self.updated_json_files,
            "errors": self.errors,
        }


def main() -> None:
    CreateWorkspaceStructureEndpointScript().run()


if __name__ == "__main__":
    main()
