"""CCore developer command entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ensure_backend_on_path(project_root: Path) -> None:
    backend_root = project_root / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def _resolve_database_path(project_root: Path, database_path: str | None) -> Path:
    if database_path:
        return Path(database_path).resolve()

    from src.core.shared.app_path_utils import get_path

    return get_path("database")


def _run_factory_with_config(project_root: Path, config_path: str) -> None:
    from src.core.factory.prefect_flow import run_factory_pipeline

    run_factory_pipeline(
        project_root_value=str(project_root),
        config_path_value=str(Path(config_path).resolve()),
    )


def _run_factory_pending_tasks(project_root: Path, database_path: str | None) -> None:
    from src.core.factory.task_dependencies import build_sql_task_repository
    from src.core.factory.task_runner import FactoryTaskRunner
    from src.infrastructure.orchestration.prefect.prefect_execution_provider import (
        PrefectExecutionProvider,
    )

    resolved_database_path = _resolve_database_path(project_root, database_path)
    task_repository = build_sql_task_repository(resolved_database_path)
    execution_provider = PrefectExecutionProvider()
    result = FactoryTaskRunner(
        task_repository=task_repository,
        execution_provider=execution_provider,
    ).run_pending_tasks()
    print(json.dumps(result.to_dict(), indent=2))


def _seed_factory_tasks(
    project_root: Path,
    database_path: str | None,
    seed_path: str | None,
) -> None:
    from src.core.factory.constants import DEFAULT_FACTORY_TASK_SEED_PATH
    from src.core.factory.task_dependencies import build_sql_task_repository
    from src.core.factory.task_seed_repository import JsonFactoryTaskSeedRepository
    from src.core.factory.task_seeder import FactoryTaskSeeder

    resolved_seed_path = (
        Path(seed_path).resolve()
        if seed_path
        else project_root / DEFAULT_FACTORY_TASK_SEED_PATH
    )
    seed_repository = JsonFactoryTaskSeedRepository()
    seeds = seed_repository.load_seeds(resolved_seed_path)
    resolved_database_path = _resolve_database_path(project_root, database_path)
    task_repository = build_sql_task_repository(resolved_database_path)
    result = FactoryTaskSeeder(task_repository=task_repository).seed_tasks(seeds)
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="CCore developer commands.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    factory_parser = subparsers.add_parser("factory", help="Automation Factory commands.")
    factory_subparsers = factory_parser.add_subparsers(dest="factory_command", required=True)

    run_parser = factory_subparsers.add_parser("run", help="Run pending Automation Factory tasks.")
    run_parser.add_argument("--project-root", default=None)
    run_parser.add_argument("--database", default=None)
    run_parser.add_argument("--config", default=None)

    seed_parser = factory_subparsers.add_parser("seed-tasks", help="Seed pending Factory tasks.")
    seed_parser.add_argument("--project-root", default=None)
    seed_parser.add_argument("--database", default=None)
    seed_parser.add_argument("--seed", default=None)

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path.cwd().resolve()
    _ensure_backend_on_path(project_root)

    if args.command == "factory" and args.factory_command == "run":
        if args.config:
            _run_factory_with_config(project_root, args.config)
            return
        _run_factory_pending_tasks(project_root, args.database)
        return

    if args.command == "factory" and args.factory_command == "seed-tasks":
        _seed_factory_tasks(project_root, args.database, args.seed)
        return

    parser.error("Unsupported command.")


if __name__ == "__main__":
    main()
