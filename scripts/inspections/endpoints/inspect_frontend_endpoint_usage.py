import re
from pathlib import Path
from typing import Any

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_constants import (
    STATUS_FAILED,
    STATUS_PASSED,
    STATUS_WARNING,
)
from scripts.shared.script_file_utils import read_text_file
from scripts.shared.script_json_utils import write_json_file
from scripts.shared.script_path_utils import to_relative_path


class FrontendEndpointUsageInspectionScript(BaseScript):
    def __init__(self):
        super().__init__(__file__)
        self.endpoint_pattern = self._build_endpoint_pattern()
        self.rule_id = self._get_rule_id()

    def run(self) -> None:
        findings = self._scan_frontend_files()

        result = self._build_result(findings)
        self._write_result(result)
        self._print_summary(result)

    def _build_endpoint_pattern(self) -> re.Pattern:
        endpoint_pattern = self.config.get(
            "endpointPattern",
            r"['\"](/api/[^'\"]+)['\"]",
        )

        if not isinstance(endpoint_pattern, str) or not endpoint_pattern:
            raise ValueError("Config must contain non-empty 'endpointPattern' string.")

        return re.compile(endpoint_pattern)

    def _get_rule_id(self) -> str:
        rule_id = self.config.get(
            "ruleId",
            "FRONTEND-ENDPOINT-001",
        )

        if not isinstance(rule_id, str) or not rule_id:
            raise ValueError("Config must contain non-empty 'ruleId' string.")

        return rule_id

    def _scan_frontend_files(self) -> list[dict]:
        findings = []

        for source_root in self._get_frontend_source_root_paths():
            root_path = self.project_root / source_root

            if not root_path.exists():
                continue

            findings.extend(
                self._scan_source_root(root_path),
            )

        return findings

    def _scan_source_root(
        self,
        root_path: Path,
    ) -> list[dict]:
        findings = []

        for file_path in root_path.rglob("*"):
            if not self._should_scan_file(file_path):
                continue

            findings.extend(
                self._find_endpoint_usage_findings(file_path),
            )

        return findings

    def _should_scan_file(
        self,
        file_path: Path,
    ) -> bool:
        if not file_path.is_file():
            return False

        if self._should_ignore_folder(file_path):
            return False

        if file_path.suffix not in self._get_included_file_extensions():
            return False

        if self._is_allowed_registry_file(file_path):
            return False

        return True

    def _should_ignore_folder(
        self,
        path: Path,
    ) -> bool:
        ignored_folders = self._get_ignored_folders()

        return any(part in ignored_folders for part in path.parts)

    def _is_allowed_registry_file(
        self,
        file_path: Path,
    ) -> bool:
        relative_file_path = to_relative_path(
            self.project_root,
            file_path,
        )

        return relative_file_path in self._get_allowed_endpoint_registry_files()

    def _find_endpoint_usage_findings(
        self,
        file_path: Path,
    ) -> list[dict]:
        content = read_text_file(file_path)
        matches = self.endpoint_pattern.findall(content)

        return [
            self._build_finding(
                file_path=file_path,
                endpoint=match,
            )
            for match in matches
        ]

    def _build_finding(
        self,
        file_path: Path,
        endpoint: str,
    ) -> dict:
        return {
            "ruleId": self.rule_id,
            "severity": STATUS_WARNING,
            "status": STATUS_FAILED,
            "message": (
                "Hardcoded API endpoint detected outside shared endpoint registry."
            ),
            "filePath": to_relative_path(
                self.project_root,
                file_path,
            ),
            "endpoint": endpoint,
        }

    def _build_result(
        self,
        findings: list[dict],
    ) -> dict[str, Any]:
        violation_count = len(findings)
        status = STATUS_PASSED

        if violation_count > 0:
            status = STATUS_FAILED

        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "inspect",
            ),
            "status": status,
            "violationCount": violation_count,
            "findings": findings,
        }

    def _write_result(
        self,
        result: dict,
    ) -> None:
        write_json_file(
            self._get_output_file_path(),
            result,
        )

    def _print_summary(
        self,
        result: dict,
    ) -> None:
        message = (
            "frontend endpoint usage inspection: "
            f"violations={result['violationCount']} "
            f"output={self.to_project_relative_path(self._get_output_file_path())}"
        )

        if result["status"] == STATUS_PASSED:
            print_passed(message)
            return

        print_failed(message)

    def _get_frontend_source_root_paths(self) -> list[str]:
        source_roots = self.config.get("frontendSourceRootPaths")

        if not isinstance(source_roots, list):
            raise ValueError("Config must contain 'frontendSourceRootPaths' list.")

        return source_roots

    def _get_ignored_folders(self) -> list[str]:
        ignored_folders = self.config.get("ignoredFolders", [])

        if not isinstance(ignored_folders, list):
            raise ValueError("Config 'ignoredFolders' must be a list.")

        return ignored_folders

    def _get_included_file_extensions(self) -> list[str]:
        included_extensions = self.config.get("includedFileExtensions")

        if not isinstance(included_extensions, list):
            raise ValueError("Config must contain 'includedFileExtensions' list.")

        return included_extensions

    def _get_allowed_endpoint_registry_files(self) -> list[str]:
        allowed_registry_files = self.config.get(
            "allowedEndpointRegistryFiles",
            [],
        )

        if not isinstance(allowed_registry_files, list):
            raise ValueError("Config 'allowedEndpointRegistryFiles' must be a list.")

        return allowed_registry_files

    def _get_output_file_path(self) -> Path:
        output_file_path = self.config.get("outputFilePath")

        if isinstance(output_file_path, str) and output_file_path:
            return self.project_root / output_file_path

        output_file_name = self.config.get("outputFileName")

        if isinstance(output_file_name, str) and output_file_name:
            return self.output_directory / output_file_name

        return (
            self.output_directory / f"{self.script_name}_output_{self.timestamp}.json"
        )


def main() -> None:
    try:
        FrontendEndpointUsageInspectionScript().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
