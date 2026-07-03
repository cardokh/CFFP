"""Runs the DB Pipeline test suite through the standard CFFP script architecture."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def _configure_project_import_path() -> None:
    project_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "shared").is_dir()
        ),
        None,
    )

    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_failed, print_passed
from support.db_path_utils import get_db_root, resolve_db_path


class RunDbTestsScript(BaseScript):
    """DB-local test runner for the DB Pipeline pytest contract suite."""

    def __init__(self):
        super().__init__(__file__)
        self.db_root = get_db_root(__file__)
        self.test_path = self._resolve_db_path("testPath")
        self.build_context_script_path = self._resolve_optional_db_path("buildContextScriptPath")
        self.pytest_arguments = self._get_pytest_arguments()

    def run(self) -> None:
        if self.build_context_script_path is not None:
            self._run_build_context_script()
        self._run_pytest()

    def _run_build_context_script(self) -> None:
        command = [
            sys.executable,
            str(self.build_context_script_path),
        ]

        completed = subprocess.run(
            command,
            cwd=self.project_root,
            check=False,
        )

        if completed.returncode != 0:
            print_failed("run_db_tests: DB context build failed")
            raise SystemExit(completed.returncode)

    def _run_pytest(self) -> None:
        command = [
            sys.executable,
            "-m",
            "pytest",
            str(self.test_path),
            *self.pytest_arguments,
        ]

        completed = subprocess.run(
            command,
            cwd=self.project_root,
            check=False,
        )

        if completed.returncode == 0:
            print_passed("run_db_tests: DB Pipeline tests passed")
            return

        print_failed("run_db_tests: DB Pipeline tests failed")
        raise SystemExit(completed.returncode)


    def _resolve_optional_db_path(self, config_key: str) -> Path | None:
        configured_path = self.config.get(config_key)
        if configured_path in (None, ""):
            return None
        if not isinstance(configured_path, str):
            raise ValueError(f"Config '{config_key}' must be a string when provided.")
        return resolve_db_path(self.db_root, configured_path)

    def _resolve_db_path(self, config_key: str) -> Path:
        configured_path = self.config.get(config_key)
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return resolve_db_path(self.db_root, configured_path)

    def _get_pytest_arguments(self) -> list[str]:
        pytest_arguments: Any = self.config.get("pytestArguments", [])
        if not isinstance(pytest_arguments, list):
            raise ValueError("Config key 'pytestArguments' must be a list when provided.")
        for argument in pytest_arguments:
            if not isinstance(argument, str) or not argument:
                raise ValueError("Every pytest argument must be a non-empty string.")
        return pytest_arguments


if __name__ == "__main__":
    RunDbTestsScript().run()
