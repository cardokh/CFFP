"""
Generic endpoint test runner.

Responsibilities:
- Read endpoint test definitions from JSON config.
- Execute all configured endpoint test suites in order.
- Support runtime values captured from earlier endpoint responses.
- Write one summary output file.
- Write one detailed output file per endpoint.
- Keep summary output lightweight and navigational.
- Keep endpoint detail output diagnostic-focused.
"""

from datetime import datetime

from endpoint_config import load_endpoint_test_config
from endpoint_output_writer import (
    build_output_folder,
    is_endpoint_result_successful,
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
        if not is_endpoint_result_successful(result)
    )


def determine_test_status(
    failed_count: int,
) -> str:
    return "PASSED" if failed_count == 0 else "FAILED"


def print_endpoint_result(
    result: dict,
) -> None:
    status = "PASS" if is_endpoint_result_successful(result) else "FAIL"

    print(
        f"{status} {result['method']} {result['configuredPath']} {result['name']}"
    )


def print_test_summary(
    results: list,
    failed_count: int,
    summary_output_file,
):
    status = determine_test_status(
        failed_count,
    )

    print(
        f"{status} endpoint tests: "
        f"total={len(results)} "
        f"failed={failed_count} "
        f"summary={summary_output_file}"
    )


def build_suite_endpoints(
    suite_config: dict,
) -> list:
    return [
        {
            **endpoint,
            "suite": suite_config["name"],
        }
        for endpoint in suite_config["endpoints"]
    ]


def run_endpoint_suites(
    config: dict,
    runtime_values: dict,
) -> list:
    results = []

    for suite_config in config["testSuites"]:
        for endpoint in build_suite_endpoints(
            suite_config,
        ):
            result = run_endpoint_test(
                suite_config["baseUrl"],
                endpoint,
                runtime_values,
            )

            results.append(
                result,
            )

            print_endpoint_result(
                result,
            )

    return results


def main():
    config = load_endpoint_test_config(__file__)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    runtime_values = build_runtime_values(
        timestamp,
    )

    output_folder = build_output_folder(
        config,
    )

    results = run_endpoint_suites(
        config,
        runtime_values,
    )

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
