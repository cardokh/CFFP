"""Shared path helpers for DB contract tests."""

from __future__ import annotations

from pathlib import Path


def get_db_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (
            (parent / "run_db_tasks.py").is_file()
            and (parent / "metadata").is_dir()
            and (parent / "implementations").is_dir()
        ):
            return parent
    raise RuntimeError("Could not locate DB module root.")


def get_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "scripts" / "shared").is_dir():
            return parent
    raise RuntimeError("Could not locate repository root containing scripts/shared.")


def get_postgres_root() -> Path:
    return get_db_root() / "implementations" / "postgres"


def to_db_relative(path: Path) -> str:
    return path.resolve().relative_to(get_db_root().resolve()).as_posix()


def to_project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(get_project_root().resolve()).as_posix()
    except ValueError:
        return str(path)
