"""Seed SQL-backed Automation Factory tasks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.core.factory.constants import DEFAULT_FACTORY_TASK_SEED_PATH
from src.core.factory.task_dependencies import build_sql_task_repository
from src.core.factory.task_seed_repository import JsonFactoryTaskSeedRepository
from src.core.factory.task_seeder import FactoryTaskSeeder
from src.core.shared.app_path_utils import get_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed SQL-backed Automation Factory tasks.")
    parser.add_argument("--database", default=None)
    parser.add_argument("--seed", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    database_path = Path(args.database).resolve() if args.database else get_path("database")
    seed_path = Path(args.seed).resolve() if args.seed else PROJECT_ROOT / DEFAULT_FACTORY_TASK_SEED_PATH

    seeds = JsonFactoryTaskSeedRepository().load_seeds(seed_path)
    repository = build_sql_task_repository(database_path)
    result = FactoryTaskSeeder(task_repository=repository).seed_tasks(seeds)

    print(f"Seeded {result['seeded_count']} Factory task(s).")


if __name__ == "__main__":
    main()
