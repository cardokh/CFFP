"""Prefect compatibility helpers."""

from __future__ import annotations

import sys
from typing import Any

try:
    from prefect import flow, get_run_logger, task
except ImportError:

    def task(*_args: Any, **_kwargs: Any):  # type: ignore[no-redef]
        def decorator(func):
            return func

        return decorator

    def flow(*_args: Any, **_kwargs: Any):  # type: ignore[no-redef]
        def decorator(func):
            return func

        return decorator

    def get_run_logger():  # type: ignore[no-redef]
        class ConsoleLogger:
            def info(self, message: str, *args: Any) -> None:
                print(message % args if args else message)

            def error(self, message: str, *args: Any) -> None:
                print(message % args if args else message, file=sys.stderr)

        return ConsoleLogger()
