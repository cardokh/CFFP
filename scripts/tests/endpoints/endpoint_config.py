import json
from pathlib import Path

from endpoint_constants import (
    ENDPOINT_TEST_CONFIG_FILE_NAME,
    ENDPOINT_TEST_CONFIG_FOLDER_NAME,
)


def get_endpoint_test_config_folder_path(script_file_path: str) -> Path:
    return Path(script_file_path).parent / ENDPOINT_TEST_CONFIG_FOLDER_NAME


def get_endpoint_test_config_file_path(script_file_path: str) -> Path:
    return get_endpoint_test_config_folder_path(script_file_path) / ENDPOINT_TEST_CONFIG_FILE_NAME


def load_json_file(config_path: Path) -> dict:
    with open(
        config_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_endpoint_suite_config(
    config_folder_path: Path,
    suite_definition: dict,
    root_config: dict,
) -> dict:
    suite_config_path = config_folder_path / suite_definition["configFile"]

    suite_config = load_json_file(
        suite_config_path,
    )

    suite_config["name"] = suite_definition["name"]

    suite_config["baseUrl"] = suite_config.get(
        "baseUrl",
        root_config["baseUrl"],
    )

    suite_config["outputFolder"] = suite_config.get(
        "outputFolder",
        root_config["outputFolder"],
    )

    return suite_config


def load_endpoint_test_config(script_file_path: str) -> dict:
    config_folder_path = get_endpoint_test_config_folder_path(
        script_file_path,
    )

    root_config_path = get_endpoint_test_config_file_path(
        script_file_path,
    )

    root_config = load_json_file(
        root_config_path,
    )

    if "testSuites" not in root_config:
        root_config["testSuites"] = [
            {
                "name": root_config.get(
                    "name",
                    "Default Endpoint Suite",
                ),
                "endpoints": root_config.get(
                    "endpoints",
                    [],
                ),
                "baseUrl": root_config["baseUrl"],
                "outputFolder": root_config["outputFolder"],
            }
        ]

        return root_config

    root_config["testSuites"] = [
        load_endpoint_suite_config(
            config_folder_path,
            suite_definition,
            root_config,
        )
        for suite_definition in root_config["testSuites"]
    ]

    return root_config
