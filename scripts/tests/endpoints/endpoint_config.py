import json
from pathlib import Path

from endpoint_constants import (
    ENDPOINT_TEST_CONFIG_FILE_NAME,
    ENDPOINT_TEST_CONFIG_FOLDER_NAME,
)


def get_endpoint_test_config_file_path(script_file_path: str) -> Path:
    return (
        Path(script_file_path).parent
        / ENDPOINT_TEST_CONFIG_FOLDER_NAME
        / ENDPOINT_TEST_CONFIG_FILE_NAME
    )


def load_endpoint_test_config(script_file_path: str) -> dict:
    config_path = get_endpoint_test_config_file_path(script_file_path)

    with open(
        config_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)
