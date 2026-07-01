"""Database-generation stage path helpers.

The engine stage owns reusable logic. Application-specific input, metadata,
generated files, validation output, and reports live under the Epic Tracker
application stage folder declared by each task configuration.
"""

from pathlib import Path
from typing import Any


_APPLICATION_STAGE_ROOT_KEY = "applicationStageRoot"


def get_db_root(start_path: str | Path) -> Path:
    """Return the database-generation engine stage root for a file or folder below it."""
    current = Path(start_path).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (
            candidate.name == "04_database_generation"
            and (candidate / "metadata").is_dir()
            and (candidate / "implementations").is_dir()
        ):
            return candidate

    raise RuntimeError(f"Could not locate database-generation stage root from: {start_path}")


def get_epic_tracker_root(start_path: str | Path) -> Path:
    """Return the Epic Tracker module root."""
    current = Path(start_path).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (
            candidate.name == "epic_tracker"
            and (candidate / "applications").is_dir()
            and (candidate / "engine").is_dir()
        ):
            return candidate

    raise RuntimeError(f"Could not locate epic_tracker root from: {start_path}")


def get_application_stage_root(db_root: Path, config: dict[str, Any]) -> Path:
    """Resolve the configured application stage root.

    Relative values are resolved from the Epic Tracker module root, not from the
    task folder. This keeps task configuration independent of folder depth.
    """
    configured_path = config.get(_APPLICATION_STAGE_ROOT_KEY)
    if not isinstance(configured_path, str) or not configured_path:
        raise ValueError(f"Config must contain non-empty '{_APPLICATION_STAGE_ROOT_KEY}'.")

    path = Path(configured_path)
    if path.is_absolute():
        return path
    return get_epic_tracker_root(db_root) / path


def resolve_db_path(db_root: Path, configured_path: str) -> Path:
    """Resolve absolute paths unchanged and relative paths against the engine stage root."""
    path = Path(configured_path)
    return path if path.is_absolute() else db_root / path


def resolve_application_stage_path(db_root: Path, config: dict[str, Any], configured_path: str) -> Path:
    """Resolve a path inside the configured application stage root."""
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return get_application_stage_root(db_root, config) / path


def resolve_application_stage_config_path(db_root: Path, config: dict[str, Any], config_key: str) -> Path:
    """Resolve a config value as a path inside the configured application stage root."""
    configured_path = config.get(config_key)
    if not isinstance(configured_path, str) or not configured_path:
        raise ValueError(f"Config must contain non-empty '{config_key}'.")
    return resolve_application_stage_path(db_root, config, configured_path)


def to_db_relative_path(db_root: Path, path: Path) -> str:
    """Return an engine-stage-root-relative path when possible."""
    try:
        return path.resolve().relative_to(db_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def to_application_stage_relative_path(db_root: Path, config: dict[str, Any], path: Path) -> str:
    """Return an application-stage-root-relative path when possible."""
    try:
        return path.resolve().relative_to(get_application_stage_root(db_root, config).resolve()).as_posix()
    except ValueError:
        return str(path)
