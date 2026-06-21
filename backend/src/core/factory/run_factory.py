"""Compatibility entry point for Factory task execution.

The primary entry point is:
    python ccore.py factory run

This file remains only to avoid breaking existing local commands while the
project transitions to the CCore command entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_project_on_path() -> Path:
    project_root = Path(__file__).resolve().parents[4]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


def main() -> None:
    project_root = _ensure_project_on_path()
    from ccore import main as ccore_main

    sys.argv = [
        "ccore.py",
        "factory",
        "run",
        "--project-root",
        str(project_root),
    ]
    ccore_main()


if __name__ == "__main__":
    main()
