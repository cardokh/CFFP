from pathlib import Path


def get_config_file_path(
    current_file_path: str,
) -> Path:
    return (
        Path(current_file_path).parent
        / "config"
        / f"{Path(current_file_path).stem}.json"
    )
