"""
Create a folder from a CCore execution configuration payload.

Responsibilities:
- Accept a generated execution configuration JSON file.
- Resolve the configured folder path relative to the project root unless it is absolute.
- Create the requested folder using pathlib.
- Emit a single JSON outcome line to stdout for the execution report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TRUE_VALUES = {"1", "true", "yes", "y", "on"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a folder for a CCore execution target.")
    parser.add_argument("--config", required=True, help="Path to the generated execution configuration JSON file.")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    payload = _read_json(config_path)
    elements = payload.get("configurationElements", {})

    folder_path_value = str(elements.get("folderPath", "")).strip()
    if not folder_path_value:
        raise ValueError("Configuration element 'folderPath' is required.")

    project_root = _resolve_project_root()
    requested_path = Path(folder_path_value)
    folder_path = requested_path if requested_path.is_absolute() else project_root / requested_path
    folder_path = folder_path.resolve()

    create_parents = _to_bool(elements.get("createParents", "true"))
    existed_before = folder_path.exists()

    folder_path.mkdir(parents=create_parents, exist_ok=True)

    if not folder_path.is_dir():
        raise RuntimeError(f"Folder path does not exist after create attempt: {folder_path}")

    print(
        json.dumps(
            {
                "operation": "create_folder",
                "folderPath": str(folder_path),
                "folderPathInput": folder_path_value,
                "created": not existed_before,
                "existedBefore": existed_before,
                "createParents": create_parents,
            },
            sort_keys=True,
        )
    )
    return 0


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Execution configuration payload must be a JSON object.")
    return data


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in TRUE_VALUES


def _resolve_project_root() -> Path:
    current_path = Path(__file__).resolve()
    for candidate in [current_path, *current_path.parents]:
        if (candidate / "backend").is_dir() and (candidate / "scripts").is_dir():
            return candidate
    raise RuntimeError("Could not resolve CFFP project root from create_folder.py.")


if __name__ == "__main__":
    raise SystemExit(main())
