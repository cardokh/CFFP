import ast
from pathlib import Path
from typing import Any

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_constants import ROUTE_TYPE_KEYS
from scripts.shared.script_file_utils import read_text_file
from scripts.shared.script_json_utils import write_json_file
from scripts.shared.script_path_utils import to_relative_path


class BackendEndpointExtractionScript(BaseScript):
    def __init__(self):
        super().__init__(__file__)

    def run(self) -> None:
        endpoints = self._extract_backend_route_entries()

        output = self._build_output(endpoints)
        self._write_output(output)
        self._print_success(output)

    def _extract_backend_route_entries(self) -> list[dict]:
        path_constants = self._load_api_path_constants()

        route_entries = []

        for route_registry_file in self._get_route_registry_files():
            file_path = self.project_root / route_registry_file

            route_entries.extend(
                self._extract_route_entries_from_file(
                    file_path,
                    path_constants,
                )
            )

        return self._deduplicate_route_entries(route_entries)

    def _load_api_path_constants(self) -> dict:
        constants = {}

        for api_path_file in self._get_api_path_files():
            file_path = self.project_root / api_path_file

            constants.update(
                self._extract_api_path_constants_from_file(file_path),
            )

        return constants

    def _extract_api_path_constants_from_file(
        self,
        file_path: Path,
    ) -> dict:
        tree = self._parse_python_file(file_path)
        constants = {}

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue

            if len(node.targets) != 1:
                continue

            target = node.targets[0]

            if not isinstance(target, ast.Name):
                continue

            if not target.id.startswith("API_PATH_"):
                continue

            value = self._read_string_value(node.value)

            if value is None:
                continue

            constants[target.id] = value

        return constants

    def _extract_route_entries_from_file(
        self,
        file_path: Path,
        path_constants: dict,
    ) -> list[dict]:
        tree = self._parse_python_file(file_path)
        route_entries = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Return):
                continue

            if not isinstance(node.value, ast.Dict):
                continue

            route_entries.extend(
                self._extract_route_entries_from_dict(
                    dictionary_node=node.value,
                    path_constants=path_constants,
                    source_file=file_path,
                )
            )

        return route_entries

    def _extract_route_entries_from_dict(
        self,
        dictionary_node: ast.Dict,
        path_constants: dict,
        source_file: Path,
    ) -> list[dict]:
        route_entries = []

        for method_key_node, method_value_node in zip(
            dictionary_node.keys,
            dictionary_node.values,
        ):
            method = self._extract_http_method_name(method_key_node)

            if method is None:
                continue

            if not isinstance(method_value_node, ast.Dict):
                continue

            route_entries.extend(
                self._extract_route_entries_for_method(
                    method=method,
                    method_value_node=method_value_node,
                    path_constants=path_constants,
                    source_file=source_file,
                )
            )

        return route_entries

    def _extract_route_entries_for_method(
        self,
        method: str,
        method_value_node: ast.Dict,
        path_constants: dict,
        source_file: Path,
    ) -> list[dict]:
        route_entries = []

        for route_type_key_node, route_type_value_node in zip(
            method_value_node.keys,
            method_value_node.values,
        ):
            route_type = self._extract_route_type_name(route_type_key_node)

            if route_type is None:
                continue

            if not isinstance(route_type_value_node, ast.Dict):
                continue

            route_entries.extend(
                self._extract_route_entries_for_route_type(
                    method=method,
                    route_type=route_type,
                    route_type_value_node=route_type_value_node,
                    path_constants=path_constants,
                    source_file=source_file,
                )
            )

        return route_entries

    def _extract_route_entries_for_route_type(
        self,
        method: str,
        route_type: str,
        route_type_value_node: ast.Dict,
        path_constants: dict,
        source_file: Path,
    ) -> list[dict]:
        route_entries = []

        for path_key_node in route_type_value_node.keys:
            path_constant_name = self._extract_path_constant_name(path_key_node)

            if path_constant_name is None:
                continue

            path = path_constants.get(path_constant_name)

            if path is None:
                continue

            route_entries.append(
                {
                    "method": method,
                    "routeType": route_type,
                    "path": path,
                    "pathConstant": path_constant_name,
                    "sourceFile": to_relative_path(
                        self.project_root,
                        source_file,
                    ),
                }
            )

        return route_entries

    def _parse_python_file(
        self,
        file_path: Path,
    ) -> ast.AST:
        return ast.parse(
            read_text_file(file_path),
        )

    def _read_string_value(
        self,
        node: ast.AST,
    ) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value

        return None

    def _extract_http_method_name(
        self,
        node: ast.AST,
    ) -> str | None:
        if isinstance(node, ast.Name):
            return node.id.replace("HTTP_METHOD_", "")

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value.upper()

        return None

    def _extract_route_type_name(
        self,
        node: ast.AST,
    ) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in ROUTE_TYPE_KEYS:
                return node.value

        return None

    def _extract_path_constant_name(
        self,
        node: ast.AST,
    ) -> str | None:
        if isinstance(node, ast.Name) and node.id.startswith("API_PATH_"):
            return node.id

        return None

    def _deduplicate_route_entries(
        self,
        route_entries: list[dict],
    ) -> list[dict]:
        unique_entries = {}

        for entry in route_entries:
            key = (
                entry["method"],
                entry["routeType"],
                entry["path"],
            )

            unique_entries[key] = entry

        return sorted(
            unique_entries.values(),
            key=lambda item: (
                item["path"],
                item["method"],
                item["routeType"],
            ),
        )

    def _build_output(
        self,
        endpoints: list[dict],
    ) -> dict[str, Any]:
        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "extract",
            ),
            "routeRegistryFiles": self._get_route_registry_files(),
            "apiPathFiles": self._get_api_path_files(),
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
                "backend endpoint extraction: "
                f"routeRegistries={len(output['routeRegistryFiles'])} "
                f"apiPathFiles={len(output['apiPathFiles'])} "
                f"count={output['endpointCount']} "
                f"output={self.to_project_relative_path(self._get_output_file_path())}"
            )
        )

    def _get_route_registry_files(self) -> list[str]:
        route_registry_files = self.config.get("routeRegistryFiles")

        if not isinstance(route_registry_files, list):
            raise ValueError("Config must contain 'routeRegistryFiles' list.")

        return route_registry_files

    def _get_api_path_files(self) -> list[str]:
        api_path_files = self.config.get("apiPathFiles")

        if not isinstance(api_path_files, list):
            raise ValueError("Config must contain 'apiPathFiles' list.")

        return api_path_files

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
        BackendEndpointExtractionScript().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
