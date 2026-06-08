from pathlib import Path
from typing import Any

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_constants import STATUS_PASSED
from scripts.shared.script_file_utils import read_text_file
from scripts.shared.script_json_utils import (
    read_json_file,
    write_json_file,
)
from scripts.shared.script_path_utils import to_relative_path


class BackendEndpointUsageAnalysisScript(BaseScript):
    def __init__(self):
        super().__init__(__file__)

    def run(self) -> None:
        analysis = self._execute_analysis()
        result = self._build_result(analysis)

        self._write_result(result)
        self._print_summary(result)

    def _execute_analysis(self) -> dict[str, Any]:
        frontend_contract = read_json_file(
            self._get_frontend_endpoints_path(),
        )

        backend_contract = read_json_file(
            self._get_backend_endpoints_path(),
        )

        frontend_paths = self._get_endpoint_paths(frontend_contract)
        backend_paths = self._get_endpoint_paths(backend_contract)

        frontend_path_set = {self._normalize_path(path) for path in frontend_paths}

        expected_backend_only_set = {
            self._normalize_path(path)
            for path in self._get_expected_backend_only_endpoints()
        }

        frontend_files = self._read_frontend_source_files()

        classifications = self._classify_backend_endpoints(
            backend_paths=backend_paths,
            frontend_path_set=frontend_path_set,
            expected_backend_only_set=expected_backend_only_set,
            frontend_files=frontend_files,
        )

        return {
            "frontendPaths": frontend_paths,
            "backendPaths": backend_paths,
            "usedByFrontend": classifications["usedByFrontend"],
            "expectedBackendOnly": classifications["expectedBackendOnly"],
            "possiblyUnusedOrFutureEndpoint": (
                classifications["possiblyUnusedOrFutureEndpoint"]
            ),
        }

    def _classify_backend_endpoints(
        self,
        backend_paths: list[str],
        frontend_path_set: set[str],
        expected_backend_only_set: set[str],
        frontend_files: list[dict],
    ) -> dict[str, list[dict]]:
        used_by_frontend = []
        expected_backend_only = []
        possibly_unused = []

        for backend_path in backend_paths:
            record = self._classify_backend_endpoint(
                backend_path=backend_path,
                frontend_path_set=frontend_path_set,
                expected_backend_only_set=expected_backend_only_set,
                frontend_files=frontend_files,
            )

            classification = record["classification"]

            if classification == "usedByFrontend":
                used_by_frontend.append(record)

            elif classification == "expectedBackendOnly":
                expected_backend_only.append(record)

            else:
                possibly_unused.append(record)

        return {
            "usedByFrontend": used_by_frontend,
            "expectedBackendOnly": expected_backend_only,
            "possiblyUnusedOrFutureEndpoint": possibly_unused,
        }

    def _build_result(
        self,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        used_by_frontend = analysis["usedByFrontend"]
        expected_backend_only = analysis["expectedBackendOnly"]
        possibly_unused = analysis["possiblyUnusedOrFutureEndpoint"]

        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "analyze",
            ),
            "status": STATUS_PASSED,
            "backendEndpointCount": len(analysis["backendPaths"]),
            "frontendEndpointCount": len(analysis["frontendPaths"]),
            "usedByFrontendCount": len(used_by_frontend),
            "expectedBackendOnlyCount": len(expected_backend_only),
            "possiblyUnusedOrFutureEndpointCount": len(possibly_unused),
            "usedByFrontend": used_by_frontend,
            "expectedBackendOnly": expected_backend_only,
            "possiblyUnusedOrFutureEndpoint": possibly_unused,
        }

    def _get_endpoint_paths(
        self,
        contract: dict,
    ) -> list[str]:
        endpoints = contract.get("endpoints", [])
        paths = []

        for endpoint in endpoints:
            if isinstance(endpoint, str):
                paths.append(endpoint)

            elif isinstance(endpoint, dict) and "path" in endpoint:
                paths.append(endpoint["path"])

        return sorted(set(paths))

    def _normalize_path(
        self,
        endpoint: str,
    ) -> str:
        return endpoint.rstrip("/") if endpoint != "/" else endpoint

    def _read_frontend_source_files(self) -> list[dict]:
        contents = []

        for source_root in self._get_frontend_source_root_paths():
            root_path = self.project_root / source_root

            if not root_path.exists():
                continue

            contents.extend(
                self._read_frontend_source_files_from_root(root_path),
            )

        return contents

    def _read_frontend_source_files_from_root(
        self,
        root_path: Path,
    ) -> list[dict]:
        contents = []

        for file_path in root_path.rglob("*"):
            if not self._should_read_frontend_file(file_path):
                continue

            contents.append(
                {
                    "path": to_relative_path(
                        self.project_root,
                        file_path,
                    ),
                    "content": read_text_file(file_path),
                }
            )

        return contents

    def _should_read_frontend_file(
        self,
        file_path: Path,
    ) -> bool:
        if not file_path.is_file():
            return False

        if self._should_ignore_folder(file_path):
            return False

        if file_path.suffix not in self._get_frontend_included_file_extensions():
            return False

        if self._should_exclude_frontend_usage_file(file_path):
            return False

        return True

    def _should_ignore_folder(
        self,
        path: Path,
    ) -> bool:
        ignored_folders = self._get_ignored_folders()

        return any(part in ignored_folders for part in path.parts)

    def _should_exclude_frontend_usage_file(
        self,
        file_path: Path,
    ) -> bool:
        relative_file_path = to_relative_path(
            self.project_root,
            file_path,
        )

        return relative_file_path in self._get_excluded_frontend_usage_files()

    def _classify_backend_endpoint(
        self,
        backend_path: str,
        frontend_path_set: set[str],
        expected_backend_only_set: set[str],
        frontend_files: list[dict],
    ) -> dict:
        normalized_backend_path = self._normalize_path(backend_path)

        usage_files = self._find_frontend_usage(
            backend_path,
            frontend_files,
        )

        record = {
            "path": backend_path,
            "normalizedPath": normalized_backend_path,
            "declaredInFrontendContract": (
                normalized_backend_path in frontend_path_set
            ),
            "usedByFrontendSource": len(usage_files) > 0,
            "frontendUsageFiles": usage_files,
        }

        if normalized_backend_path in expected_backend_only_set:
            record["classification"] = "expectedBackendOnly"

        elif record["declaredInFrontendContract"] or record["usedByFrontendSource"]:
            record["classification"] = "usedByFrontend"

        else:
            record["classification"] = "possiblyUnusedOrFutureEndpoint"

        return record

    def _find_frontend_usage(
        self,
        endpoint_path: str,
        frontend_files: list[dict],
    ) -> list[str]:
        matches = []
        normalized_endpoint_path = self._normalize_path(endpoint_path)

        for frontend_file in frontend_files:
            content = frontend_file["content"]

            if endpoint_path in content or normalized_endpoint_path in content:
                matches.append(frontend_file["path"])

        return sorted(set(matches))

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
        print_passed(
            (
                "backend endpoint usage analysis: "
                f"usedByFrontend={result['usedByFrontendCount']} "
                f"expectedBackendOnly={result['expectedBackendOnlyCount']} "
                f"possiblyUnused="
                f"{result['possiblyUnusedOrFutureEndpointCount']} "
                f"output={self.to_project_relative_path(self._get_output_file_path())}"
            )
        )

    def _get_frontend_endpoints_path(self) -> Path:
        frontend_endpoints_path = self.config.get("frontendEndpointsPath")

        if not isinstance(frontend_endpoints_path, str) or not frontend_endpoints_path:
            raise ValueError("Config must contain 'frontendEndpointsPath'.")

        return self.project_root / frontend_endpoints_path

    def _get_backend_endpoints_path(self) -> Path:
        backend_endpoints_path = self.config.get("backendEndpointsPath")

        if not isinstance(backend_endpoints_path, str) or not backend_endpoints_path:
            raise ValueError("Config must contain 'backendEndpointsPath'.")

        return self.project_root / backend_endpoints_path

    def _get_frontend_source_root_paths(self) -> list[str]:
        source_roots = self.config.get("frontendSourceRootPaths")

        if not isinstance(source_roots, list):
            raise ValueError("Config must contain 'frontendSourceRootPaths' list.")

        return source_roots

    def _get_frontend_included_file_extensions(self) -> list[str]:
        included_extensions = self.config.get("frontendIncludedFileExtensions")

        if not isinstance(included_extensions, list):
            raise ValueError(
                "Config must contain 'frontendIncludedFileExtensions' list."
            )

        return included_extensions

    def _get_ignored_folders(self) -> list[str]:
        ignored_folders = self.config.get("ignoredFolders", [])

        if not isinstance(ignored_folders, list):
            raise ValueError("Config 'ignoredFolders' must be a list.")

        return ignored_folders

    def _get_excluded_frontend_usage_files(self) -> list[str]:
        excluded_files = self.config.get(
            "excludedFrontendUsageFiles",
            [],
        )

        if not isinstance(excluded_files, list):
            raise ValueError("Config 'excludedFrontendUsageFiles' must be a list.")

        return excluded_files

    def _get_expected_backend_only_endpoints(self) -> list[str]:
        expected_backend_only_endpoints = self.config.get(
            "expectedBackendOnlyEndpoints",
            [],
        )

        if not isinstance(expected_backend_only_endpoints, list):
            raise ValueError("Config 'expectedBackendOnlyEndpoints' must be a list.")

        return expected_backend_only_endpoints

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
        BackendEndpointUsageAnalysisScript().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
