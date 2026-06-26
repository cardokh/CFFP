"""Config loading helpers for backend CRUD automation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def resolve_repo_root(config: dict[str, Any], config_path: Path) -> Path:
    configured_root = Path(str(config.get("repoRoot", ".")))
    if configured_root.is_absolute():
        return configured_root.resolve()
    return (config_path.parent / configured_root).resolve()
