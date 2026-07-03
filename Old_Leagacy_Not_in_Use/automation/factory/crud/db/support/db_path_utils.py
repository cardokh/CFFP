"""DB-module path helpers.

These helpers keep DB task configuration portable inside the DB module while
still allowing every script to use the shared BaseScript infrastructure.
"""

from pathlib import Path


def get_db_root(start_path: str | Path) -> Path:
    """Return the DB module root for a file or folder below db/."""
    current = Path(start_path).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (
            (candidate / "run_db_tasks.py").is_file()
            and (candidate / "config").is_dir()
            and (candidate / "metadata").is_dir()
            and (candidate / "implementations").is_dir()
        ):
            return candidate

    raise RuntimeError(f"Could not locate DB module root from: {start_path}")


def resolve_db_path(db_root: Path, configured_path: str) -> Path:
    """Resolve absolute paths unchanged and relative paths against db_root."""
    path = Path(configured_path)
    return path if path.is_absolute() else db_root / path


def to_db_relative_path(db_root: Path, path: Path) -> str:
    """Return a DB-root-relative path when possible."""
    try:
        return path.resolve().relative_to(db_root.resolve()).as_posix()
    except ValueError:
        return str(path)
