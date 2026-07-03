"""Generate CCore frontend CRUD modules from the existing Tasks module golden template."""
from __future__ import annotations

import argparse
from pathlib import Path

from generator_lib.config_loader import load_config
from generator_lib.frontend_generator import FrontendCrudGenerator
from generator_lib.report_writer import write_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate CCore frontend CRUD files.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument(
        "--config",
        default="automation/factory/crud/frontend/config/generate_frontend.json",
        help="Frontend CRUD generator configuration file.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    config_path = repo_root / args.config
    config = load_config(config_path)

    result = FrontendCrudGenerator(repo_root=repo_root, config=config).generate()
    write_report(repo_root / config.paths.report, result)

    print(f"Generated {len(result.written_files)} frontend CRUD file(s).")
    print(f"Report: {config.paths.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
