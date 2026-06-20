"""Automation Factory command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .prefect_flow import run_factory_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CCore Automation Factory.")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Optional path to factory_config.json.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the Factory CLI."""

    args = parse_args()
    project_root = str(Path(args.project_root).resolve()) if args.project_root else None
    config_path = str(Path(args.config).resolve()) if args.config else None
    run_factory_pipeline(project_root_value=project_root, config_path_value=config_path)
