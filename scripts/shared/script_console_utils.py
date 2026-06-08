from scripts.shared.script_constants import (
    STATUS_ERROR,
    STATUS_FAILED,
    STATUS_PASSED,
    STATUS_SKIPPED,
    STATUS_WARNING,
)


def print_status(
    status: str,
    message: str,
):
    print(f"{status} {message}")


def print_passed(message: str):
    print_status(
        STATUS_PASSED,
        message,
    )


def print_failed(message: str):
    print_status(
        STATUS_FAILED,
        message,
    )


def print_error(message: str):
    print_status(
        STATUS_ERROR,
        message,
    )


def print_warning(message: str):
    print_status(
        STATUS_WARNING,
        message,
    )


def print_skipped(message: str):
    print_status(
        STATUS_SKIPPED,
        message,
    )
