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
    endpoint_file_name = to_safe_file_name(
        f"{result.get('suite') or 'endpoint'} {result['name']}"
    )

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


def is_endpoint_result_successful(result: dict) -> bool:
    return (
        result["infrastructure"]["success"]
        and result["operation"]["success"] is not False
    )


def write_summary_output(
    output_folder: Path,
    timestamp: str,
    config: dict,
    results: list,
) -> Path:
    successful_endpoints = []

    failed_endpoints = []

    suite_summaries = {}

    for result in results:
        endpoint_name = result["name"]

        suite_name = result.get(
            "suite",
            "Default Endpoint Suite",
        )

        if suite_name not in suite_summaries:
            suite_summaries[suite_name] = {
                "totalEndpoints": 0,
                "passedEndpoints": 0,
                "failedEndpoints": 0,
            }

        suite_summaries[suite_name]["totalEndpoints"] += 1

        if is_endpoint_result_successful(result):
            successful_endpoints.append(endpoint_name)
            suite_summaries[suite_name]["passedEndpoints"] += 1

        else:
            failed_endpoints.append(endpoint_name)
            suite_summaries[suite_name]["failedEndpoints"] += 1

    summary = {
        "timestamp": timestamp,
        "baseUrl": config["baseUrl"],
        "totalEndpoints": len(results),
        "passedEndpoints": len(successful_endpoints),
        "failedEndpoints": len(failed_endpoints),
        "successfulEndpointNames": successful_endpoints,
        "failedEndpointNames": failed_endpoints,
        "suiteSummaries": suite_summaries,
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
