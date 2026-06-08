import re
from pathlib import Path
from typing import Any

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_file_utils import read_text_file
from scripts.shared.script_json_utils import write_json_file
from scripts.shared.script_path_utils import to_relative_path


class FrontendEndpointExtractionScript(BaseScript):
    def __init__(self):
        super().__init__(__file__)
        self.endpoint_pattern = self._build_endpoint_pattern()

    def run(self) -> None:
        endpoints = self._extract_endpoints()

        output = self._build_output(endpoints)
        self._write_output(output)
        self._print_success(output)

    def _build_endpoint_pattern(self) -> re.Pattern:
        endpoint_pattern = self.config.get(
            "endpointPattern",
            r"['\"](/api/[^'\"]+)['\"]",
        )

        if not isinstance(endpoint_pattern, str) or not endpoint_pattern:
            raise ValueError("Config must contain non-empty 'endpointPattern' string.")

        return re.compile(endpoint_pattern)

    def _extract_endpoints(self) -> list[str]:
        content = read_text_file(
            self._get_source_file_path(),
        )

        return sorted(
            set(
                self.endpoint_pattern.findall(
                    content,
                )
            )
        )

    def _build_output(
        self,
        endpoints: list[str],
    ) -> dict[str, Any]:
        source_file_path = self._get_source_file_path()

        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "extract",
            ),
            "sourceFile": to_relative_path(
                self.project_root,
                source_file_path,
            ),
            "endpointCount": len(endpoints),
            "endpoints": endpoints,
        }

    def _write_output(
        self,
        output: dict,
    ) -> None:
        output_file_path = self._get_output_file_path()

        write_json_file(
            output_file_path,
            output,
        )

    def _print_success(
        self,
        output: dict,
    ) -> None:
        print_passed(
            (
                "frontend endpoint extraction: "
                f"count={output['endpointCount']} "
                f"output={self.to_project_relative_path(self._get_output_file_path())}"
            )
        )

    def _get_source_file_path(self) -> Path:
        source_file_path = self.config.get("sourceFilePath")

        if not isinstance(source_file_path, str) or not source_file_path:
            raise ValueError("Config must contain 'sourceFilePath'.")

        return self.project_root / source_file_path

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
        FrontendEndpointExtractionScript().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
