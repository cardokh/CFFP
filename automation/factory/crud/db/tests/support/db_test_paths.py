"""Shared path helpers for DB pipeline contract tests."""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """Return the repository root containing automation/factory/crud/db."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "automation" / "factory" / "crud" / "db").is_dir():
            return parent
    raise RuntimeError("Could not locate repository root containing automation/factory/crud/db.")


def get_db_root() -> Path:
    return get_project_root() / "automation" / "factory" / "crud" / "db"


def get_postgres_root() -> Path:
    return get_db_root() / "postgres"


def to_project_relative(path: Path) -> str:
    return path.resolve().relative_to(get_project_root().resolve()).as_posix()
