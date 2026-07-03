"""Pytest path setup for DB-local tests."""

from pathlib import Path
import sys

DB_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "run_db_tasks.py").is_file()
    and (parent / "metadata").is_dir()
    and (parent / "implementations").is_dir()
)
PROJECT_ROOT = next(
    (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
    None,
)

for path in [DB_ROOT, PROJECT_ROOT]:
    if path is not None and str(path) not in sys.path:
        sys.path.insert(0, str(path))
