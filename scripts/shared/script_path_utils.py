from pathlib import Path

from scripts.shared.script_config_utils import (
    get_config_file_path,
    load_config,
)

CONFIG_FILE_PATH = get_config_file_path(__file__)

CONFIG = load_config(CONFIG_FILE_PATH)


def resolve_placeholders(
    value: str,
) -> str:
    resolved_value = value
    changed = True

    while changed:
        changed = False

        for key, config_value in CONFIG.items():
            if not isinstance(
                config_value,
                str,
            ):
                continue

            placeholder = "{" + key + "}"

            if placeholder not in resolved_value:
                continue

            resolved_value = resolved_value.replace(
                placeholder,
                config_value,
            )

            changed = True

    return resolved_value


def get_path(
    key: str,
) -> Path:
    if key not in CONFIG:
        raise KeyError(f"Path key not configured: {key}")

    value = CONFIG[key]

    if not isinstance(
        value,
        str,
    ):
        raise TypeError(f"Path value must be a string: {key}")

    resolved_value = resolve_placeholders(value)

    return Path(resolved_value).resolve()


def get_project_root() -> Path:
    return get_path("projectRoot")


def to_relative_path(
    project_root: Path,
    file_path: Path,
) -> str:
    return str(file_path.relative_to(project_root)).replace(
        "\\",
        "/",
    )
