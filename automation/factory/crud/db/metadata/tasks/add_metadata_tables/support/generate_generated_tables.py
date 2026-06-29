"""Stage 1 placeholder for generated table batch creation."""

from pathlib import Path
from typing import Any


_GENERATED_TABLES_PATH_CONFIG_KEY = "generatedTablesPath"


def generate_generated_tables(script_directory: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Run the table-batch generation stage in manual placeholder mode.

    The current implementation intentionally performs no generation. The input
    batch must already exist on disk and is consumed by Stage 2.
    """

    generated_tables_path = _resolve_generated_tables_path(script_directory, config)
    if not generated_tables_path.exists():
        raise FileNotFoundError(f"Generated tables batch not found: {generated_tables_path}")

    print("Generation step skipped (manual mode).")
    return {
        "status": "SKIPPED",
        "mode": "manual",
        "message": "Generation step skipped (manual mode).",
        "generatedTablesPath": str(generated_tables_path),
        "tableCount": 0,
    }


def _resolve_generated_tables_path(script_directory: Path, config: dict[str, Any]) -> Path:
    configured_path = config.get(_GENERATED_TABLES_PATH_CONFIG_KEY, "input/generated_tables.json")
    if not isinstance(configured_path, str) or not configured_path:
        raise ValueError(f"Config must contain non-empty '{_GENERATED_TABLES_PATH_CONFIG_KEY}'.")
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return script_directory / path
