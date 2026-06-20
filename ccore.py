"""CCore developer command entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_backend_on_path(project_root: Path) -> None:
    backend_root = project_root / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def main() -> None:
    parser = argparse.ArgumentParser(description="CCore developer commands.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    factory_parser = subparsers.add_parser("factory", help="Automation Factory commands.")
    factory_subparsers = factory_parser.add_subparsers(dest="factory_command", required=True)
    run_parser = factory_subparsers.add_parser("run", help="Run the Automation Factory.")
    run_parser.add_argument("--project-root", default=None)
    run_parser.add_argument("--config", default=None)

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path.cwd().resolve()
    _ensure_backend_on_path(project_root)

    if args.command == "factory" and args.factory_command == "run":
        from src.core.factory.prefect_flow import run_factory_pipeline

        config_path = str(Path(args.config).resolve()) if args.config else None
        run_factory_pipeline(project_root_value=str(project_root), config_path_value=config_path)
        return

    parser.error("Unsupported command.")


if __name__ == "__main__":
    main()
