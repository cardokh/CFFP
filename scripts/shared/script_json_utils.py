from pathlib import Path
import json

from scripts.shared.script_constants import (
    ENCODING_UTF_8,
    JSON_INDENT,
)

from scripts.shared.script_file_utils import (
    ensure_parent_folder,
)


def read_json_file(file_path: Path) -> dict:
    with open(
        file_path,
        "r",
        encoding=ENCODING_UTF_8,
    ) as file:
        return json.load(file)


def write_json_file(
    file_path: Path,
    data: dict,
):
    ensure_parent_folder(file_path)

    with open(
        file_path,
        "w",
        encoding=ENCODING_UTF_8,
    ) as file:
        json.dump(
            data,
            file,
            indent=JSON_INDENT,
        )
