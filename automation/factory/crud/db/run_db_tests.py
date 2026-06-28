"""Run the DB Pipeline test suite.

This runner is intentionally small. Pytest remains the real test runner, but this
file gives the DB Pipeline one obvious command for running all DB-local tests.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "automation" / "factory" / "crud" / "db" / "tests").is_dir():
            return parent
    raise RuntimeError("Could not locate repository root containing automation/factory/crud/db/tests.")


def main() -> int:
    project_root = find_project_root()
    test_path = project_root / "automation" / "factory" / "crud" / "db" / "tests"
    command = [sys.executable, "-m", "pytest", str(test_path)]
    completed = subprocess.run(command, cwd=project_root, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
