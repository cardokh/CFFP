"""
Shared path utilities.

Responsibilities:
- Load centralized application paths from configuration.
- Resolve placeholder-based path variables.
- Provide reusable path lookup helpers.
- Keep filesystem path logic centralized.
"""

import json
from functools import lru_cache
from pathlib import Path
from src.core.shared.app_config_utils import (
    get_config_file_path,
)


def resolve_placeholders(data):
    resolved = dict(data)

    changed = True

    while changed:
        changed = False

        for key, value in resolved.items():
            if isinstance(value, str):
                new_value = value

                for var, var_value in resolved.items():
                    if isinstance(var_value, str):
                        placeholder = "{" + var + "}"

                        if placeholder in new_value:
                            new_value = new_value.replace(
                                placeholder,
                                var_value,
                            )

                if new_value != value:
                    resolved[key] = new_value
                    changed = True

    return resolved


@lru_cache(maxsize=1)
def load_paths():
    config_file_path = get_config_file_path(__file__)

    with open(config_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    project_root = Path(__file__).resolve().parents[4]

    data["projectRoot"] = str(project_root)

    resolved = resolve_placeholders(data)

    return {key: Path(value).resolve() for key, value in resolved.items()}


def get_path(key: str) -> Path:
    paths = load_paths()

    if key not in paths:
        raise KeyError(f"Path key not configured: {key}")

    return paths[key]
