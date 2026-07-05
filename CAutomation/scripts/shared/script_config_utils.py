from pathlib import Path

from scripts.shared.script_json_utils import read_json_file


def get_config_file_path(script_file_path: str) -> Path:
    script_path = Path(script_file_path)

    return script_path.parent / "config" / f"{script_path.stem}.json"


def load_config(config_file_path: Path) -> dict:
    return read_json_file(config_file_path)
