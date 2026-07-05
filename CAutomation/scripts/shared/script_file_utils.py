from pathlib import Path

from scripts.shared.script_constants import ENCODING_UTF_8


def read_text_file(file_path: Path) -> str:
    with open(file_path, "r", encoding=ENCODING_UTF_8) as file:
        return file.read()


def ensure_parent_folder(file_path: Path):
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
