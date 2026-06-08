"""
Generic endpoint test runner.

Responsibilities:
- Read endpoint test definitions from JSON config.
- Execute all configured endpoint tests.
- Write one summary output file.
- Write one detailed output file per endpoint.
- Keep summary output lightweight and navigational.
- Keep endpoint detail output diagnostic-focused.
"""

from datetime import datetime

from endpoint_config import load_endpoint_test_config
from endpoint_output_writer import (
    build_output_folder,
    write_endpoint_output,
    write_summary_output,
)
from endpoint_result_builder import run_endpoint_test


def build_runtime_values(
    timestamp: str,
) -> dict:
    return {
        "timestamp": timestamp,
    }


def calculate_failed_endpoint_count(
    results: list,
) -> int:
    return sum(
        1
        for result in results
        if not result["infrastructure"]["success"]
        or result["operation"]["success"] is False
    )


def determine_test_status(
    failed_count: int,
) -> str:
    return "PASSED" if failed_count == 0 else "WARNING"


def print_test_summary(
    results: list,
    failed_count: int,
    summary_output_file,
):
    status = determine_test_status(
        failed_count,
    )

    print(
        f"{status} endpoint smoke tests: "
        f"total={len(results)} "
        f"failed={failed_count} "
        f"summary={summary_output_file}"
    )


def main():
    config = load_endpoint_test_config(__file__)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    runtime_values = build_runtime_values(
        timestamp,
    )

    output_folder = build_output_folder(
        config,
    )

    results = [
        run_endpoint_test(
            config["baseUrl"],
            endpoint,
            runtime_values,
        )
        for endpoint in config["endpoints"]
    ]

    for result in results:
        write_endpoint_output(
            output_folder,
            timestamp,
            result,
        )

    summary_output_file = write_summary_output(
        output_folder,
        timestamp,
        config,
        results,
    )

    failed_count = calculate_failed_endpoint_count(
        results,
    )

    print_test_summary(
        results,
        failed_count,
        summary_output_file,
    )


if __name__ == "__main__":
    main()
