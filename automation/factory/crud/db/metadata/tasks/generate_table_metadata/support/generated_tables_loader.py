"""Loads generated table batches from JSON."""

from pathlib import Path
from typing import Any

from scripts.shared.script_json_utils import read_json_file


def load_generated_tables(generated_tables_path: Path) -> dict[str, Any]:
    """Read generated_tables.json and validate its top-level shape."""

    batch = read_json_file(generated_tables_path)
    if not isinstance(batch, dict):
        raise ValueError("Generated tables batch must contain a JSON object.")
    if "tables" not in batch:
        raise ValueError("Generated tables batch must contain a 'tables' array.")
    if not isinstance(batch["tables"], list):
        raise ValueError("Generated tables batch field 'tables' must be a list.")
    return batch
