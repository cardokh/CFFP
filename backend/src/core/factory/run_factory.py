"""Compatibility entry point for running the Automation Factory."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_backend_on_path() -> None:
    if __package__:
        return
    backend_root = Path(__file__).resolve().parents[3]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


_ensure_backend_on_path()

if __package__:
    from .cli import main
else:
    from src.core.factory.cli import main


if __name__ == "__main__":
    main()
