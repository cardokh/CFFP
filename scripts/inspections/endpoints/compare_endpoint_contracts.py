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
)
from scripts.shared.script_json_utils import (
    read_json_file,
    write_json_file,
)


class EndpointContractComparisonScript(BaseScript):
    def __init__(self):
        super().__init__(__file__)

    def run(self) -> None:
        comparison = self._build_comparison()
        self._write_output(comparison)
        self._print_summary(comparison)

    def _build_comparison(self) -> dict[str, Any]:
        frontend_contract = read_json_file(
            self._get_frontend_endpoints_path(),
        )

        backend_contract = read_json_file(
            self._get_backend_endpoints_path(),
        )

        frontend_endpoints = self._get_endpoint_paths(frontend_contract)
        backend_endpoints = self._get_endpoint_paths(backend_contract)

        matching_endpoints = sorted(
            frontend_endpoints & backend_endpoints,
        )

        frontend_missing_in_backend = sorted(
            frontend_endpoints - backend_endpoints,
        )

        backend_missing_in_frontend = sorted(
            backend_endpoints - frontend_endpoints,
        )

        status = STATUS_PASSED

        if frontend_missing_in_backend:
            status = STATUS_FAILED

        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "compare",
            ),
            "status": status,
            "frontendEndpointCount": len(frontend_endpoints),
            "backendEndpointCount": len(backend_endpoints),
            "matchingEndpointCount": len(matching_endpoints),
            "frontendMissingInBackendCount": len(frontend_missing_in_backend),
            "backendMissingInFrontendCount": len(backend_missing_in_frontend),
            "matchingEndpoints": matching_endpoints,
            "frontendMissingInBackend": frontend_missing_in_backend,
            "backendMissingInFrontend": backend_missing_in_frontend,
        }

    def _get_endpoint_paths(
        self,
        contract: dict,
    ) -> set[str]:
        endpoints = contract.get("endpoints")

        if not isinstance(endpoints, list):
            raise ValueError("Endpoint contract must contain 'endpoints' list.")

        return {self._get_endpoint_path(endpoint) for endpoint in endpoints}

    def _get_endpoint_path(
        self,
        endpoint: object,
    ) -> str:
        if isinstance(endpoint, str):
            return endpoint

        if isinstance(endpoint, dict):
            path = endpoint.get("path")

            if isinstance(path, str) and path:
                return path

        raise TypeError(f"Unsupported endpoint contract entry: {endpoint}")

    def _write_output(
        self,
        comparison: dict,
    ) -> None:
        write_json_file(
            self._get_output_file_path(),
            comparison,
        )

    def _print_summary(
        self,
        comparison: dict,
    ) -> None:
        message = (
            "endpoint contract comparison: "
            f"frontend={comparison['frontendEndpointCount']} "
            f"backend={comparison['backendEndpointCount']} "
            f"matching={comparison['matchingEndpointCount']} "
            f"frontendMissing="
            f"{comparison['frontendMissingInBackendCount']} "
            f"backendMissing="
            f"{comparison['backendMissingInFrontendCount']} "
            f"output={self.to_project_relative_path(self._get_output_file_path())}"
        )

        if comparison["status"] == STATUS_PASSED:
            print_passed(message)
            return

        print_failed(message)

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
        EndpointContractComparisonScript().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
