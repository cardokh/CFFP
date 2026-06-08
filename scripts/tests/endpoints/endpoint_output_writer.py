import json
import re
from pathlib import Path

from endpoint_constants import (
    ENDPOINT_TEST_SUMMARY_FILE_PREFIX,
    JSON_FILE_EXTENSION,
)


def to_safe_file_name(value: str) -> str:
    safe_value = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        value.lower(),
    ).strip("_")

    return safe_value or "endpoint"


def build_output_folder(
    config: dict,
) -> Path:
    output_folder = Path(config["outputFolder"])

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_folder


def write_endpoint_output(
    output_folder: Path,
    timestamp: str,
    result: dict,
) -> Path:
    endpoint_file_name = to_safe_file_name(result["name"])

    output_file_path = output_folder / (
        f"{endpoint_file_name}_{timestamp}{JSON_FILE_EXTENSION}"
    )

    with open(
        output_file_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=4,
        )

    return output_file_path


def write_summary_output(
    output_folder: Path,
    timestamp: str,
    config: dict,
    results: list,
) -> Path:
    successful_endpoints = []

    failed_endpoints = []

    for result in results:
        endpoint_name = result["name"]

        infrastructure_success = result["infrastructure"]["success"]

        operation_success = result["operation"]["success"]

        if infrastructure_success and operation_success is not False:
            successful_endpoints.append(endpoint_name)

        else:
            failed_endpoints.append(endpoint_name)

    summary = {
        "timestamp": timestamp,
        "baseUrl": config["baseUrl"],
        "totalEndpoints": len(results),
        "passedEndpoints": len(successful_endpoints),
        "failedEndpoints": len(failed_endpoints),
        "successfulEndpointNames": successful_endpoints,
        "failedEndpointNames": failed_endpoints,
        "outputFolder": str(output_folder),
    }

    output_file_path = output_folder / (
        f"{ENDPOINT_TEST_SUMMARY_FILE_PREFIX}_{timestamp}{JSON_FILE_EXTENSION}"
    )

    with open(
        output_file_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
        )

    return output_file_path
