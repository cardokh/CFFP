#!/usr/bin/env python3
"""Generate CCore backend CRUD files for pipelines."""
from __future__ import annotations

import argparse
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
from scripts.shared.script_json_utils import read_json_file

from generator_lib.backend_generator import BackendCrudGenerator


class GenerateBackendScript(BaseScript):
    """Config-driven Backend CRUD Automation entry point."""

    def __init__(
        self,
        config_path: Path | None = None,
        project_root: Path | None = None,
        write_report: bool = True,
        print_summary: bool = True,
    ):
        super().__init__(__file__)
        self.write_report_enabled = write_report
        self.print_summary_enabled = print_summary

        if project_root is not None:
            self.project_root = project_root.resolve()

        if config_path is not None:
            self.config_path = config_path.resolve()
            self.config = read_json_file(self.config_path)

    def run(self) -> dict[str, Any]:
        generator = BackendCrudGenerator(script_directory=self.script_directory)
        report = generator.generate(
            repo_root=self.project_root,
            config=self.config,
        )

        report = self._build_generation_report(report)

        if self.write_report_enabled:
            self.write_json_report(report)

        if self.print_summary_enabled:
            print_passed(
                f"{self.script_name}: generated backend CRUD for {report.get('entity')}"
            )

        return report

    def _build_generation_report(self, generator_report: dict[str, Any]) -> dict[str, Any]:
        return generator_report


def generate_backend(
    config_path: Path | None = None,
    project_root: Path | None = None,
    write_report: bool = True,
    print_summary: bool = True,
) -> dict[str, Any]:
    """Run backend generation and return the generation report."""
    return GenerateBackendScript(
        config_path=config_path,
        project_root=project_root,
        write_report=write_report,
        print_summary=print_summary,
    ).run()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate CCore pipeline backend CRUD automation output."
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Optional path to generate_backend.json. Defaults to this script's config folder.",
    )
    args = parser.parse_args()

    config_path = Path(args.config).resolve() if args.config else None
    generate_backend(config_path=config_path)


if __name__ == "__main__":
    main()
