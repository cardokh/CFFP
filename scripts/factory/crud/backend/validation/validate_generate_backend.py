#!/usr/bin/env python3
"""Validate Backend CRUD Automation for pipeline generation."""
from __future__ import annotations

import argparse
import py_compile
import shutil
import tempfile
from pathlib import Path
import sys


def _find_project_root(start_path: Path) -> Path:
    for candidate in [start_path, *start_path.parents]:
        if (candidate / "scripts" / "shared" / "base_script.py").exists():
            return candidate
    raise RuntimeError("Unable to locate CFFP project root from script path.")


def _ensure_project_root_on_path() -> None:
    project_root = _find_project_root(Path(__file__).resolve())
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_ensure_project_root_on_path()

from typing import Any

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file

BACKEND_SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
if str(BACKEND_SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_SCRIPT_DIRECTORY))

from generate_backend import generate_backend  # noqa: E402


class ValidateGenerateBackendScript(BaseScript):
    """Validates backend CRUD generation in an isolated temporary repository."""

    def __init__(self, config_path: Path | None = None):
        super().__init__(__file__)

        if config_path is not None:
            self.config_path = config_path.resolve()
            self.config = read_json_file(self.config_path)

    def run(self) -> dict[str, Any]:
        report = self._validate_backend_generation()
        self.write_json_report(report)
        print_passed(
            f"{self.script_name}: validated backend CRUD generation for {report.get('entity')}"
        )
        return report

    def _validate_backend_generation(self) -> dict[str, Any]:
        generation_config_path = self.project_root / self.config["generationConfigPath"]
        generation_config = read_json_file(generation_config_path)

        with tempfile.TemporaryDirectory(
            prefix="cffp_backend_generation_validate_"
        ) as temp_dir:
            temp_repo_root = Path(temp_dir) / "repo"
            temp_repo_root.mkdir(parents=True, exist_ok=True)
            self._copy_repo_without_heavy_dirs(self.project_root, temp_repo_root)

            temp_generation_config_path = (
                temp_repo_root / self.config["generationConfigPath"]
            )
            temp_generation_config = read_json_file(temp_generation_config_path)
            write_json_file(temp_generation_config_path, temp_generation_config)

            generation_report = generate_backend(
                config_path=temp_generation_config_path,
                project_root=temp_repo_root,
                write_report=False,
                print_summary=False,
            )

            expected_output_dir = (
                temp_repo_root / self.config["expectedOutputPackageDirectory"]
            )
            expected_files = [
                expected_output_dir / file_name
                for file_name in self.config["expectedGeneratedFiles"]
            ]

            missing_files = [
                str(path.relative_to(temp_repo_root)).replace("\\", "/")
                for path in expected_files
                if not path.exists()
            ]
            if missing_files:
                raise RuntimeError(f"Generated backend files missing: {missing_files}")

            patched_missing = [
                path
                for path in self.config["expectedPatchedFiles"]
                if not (temp_repo_root / path).exists()
            ]
            if patched_missing:
                raise RuntimeError(f"Expected patch target files missing: {patched_missing}")

            compiled_generated_files = self._compile_python_files(
                [path for path in expected_files if path.suffix == ".py"],
                temp_repo_root,
            )
            automation_python_files = list(
                (
                    temp_repo_root / self.config["automationPackageDirectory"]
                ).rglob("*.py")
            )
            compiled_automation_files = self._compile_python_files(
                automation_python_files,
                temp_repo_root,
            )

        return self._build_report(
            entity=generation_config.get("entity"),
            expected_generated_files=self.config["expectedGeneratedFiles"],
            compiled_generated_files=compiled_generated_files,
            compiled_automation_files=compiled_automation_files,
            generation_report_status=generation_report.get("status"),
        )

    def _copy_repo_without_heavy_dirs(
        self,
        repo_root: Path,
        target_root: Path,
    ) -> None:
        ignore = shutil.ignore_patterns(
            ".git",
            "__pycache__",
            "*.pyc",
            ".venv",
            "node_modules",
        )

        for item in repo_root.iterdir():
            target = target_root / item.name
            if item.is_dir():
                shutil.copytree(item, target, ignore=ignore)
            else:
                shutil.copy2(item, target)

    def _compile_python_files(
        self,
        paths: list[Path],
        relative_root: Path,
    ) -> list[str]:
        compiled: list[str] = []
        for path in paths:
            py_compile.compile(str(path), doraise=True)
            compiled.append(str(path.relative_to(relative_root)).replace("\\", "/"))
        return compiled

    def _build_report(
        self,
        entity: str | None,
        expected_generated_files: list[str],
        compiled_generated_files: list[str],
        compiled_automation_files: list[str],
        generation_report_status: str | None,
    ) -> dict[str, Any]:
        return {
            "scriptName": self.script_name,
            "status": "passed",
            "validatedAt": self.timestamp,
            "entity": entity,
            "expectedGeneratedFiles": expected_generated_files,
            "compiledGeneratedFiles": compiled_generated_files,
            "compiledAutomationFiles": compiled_automation_files,
            "generationReportStatus": generation_report_status,
        }


def validate_backend_generation(config_path: Path | None = None) -> dict[str, Any]:
    """Run backend generation validation and return the validation report."""
    return ValidateGenerateBackendScript(config_path=config_path).run()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate CCore pipeline backend CRUD automation."
    )
    parser.add_argument(
        "--config",
        default=None,
        help=(
            "Optional path to validate_generate_backend.json. "
            "Defaults to this script's config folder."
        ),
    )
    args = parser.parse_args()

    config_path = Path(args.config).resolve() if args.config else None
    validate_backend_generation(config_path=config_path)


if __name__ == "__main__":
    main()
