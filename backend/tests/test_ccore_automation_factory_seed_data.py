import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEED_DATA_PATH = PROJECT_ROOT / "scripts" / "db" / "postgres" / "config" / "postgres_seed_data.json"


EXPECTED_AUTOMATION_FACTORY_TASKS = [
    {
        "task_id": "11111111-1111-1111-1111-111111111111",
        "task_name": "Bootstrap Project",
        "status_code": "PENDING",
    },
    {
        "task_id": "22222222-2222-2222-2222-222222222222",
        "task_name": "Validate Project",
        "status_code": "PENDING",
    },
    {
        "task_id": "33333333-3333-3333-3333-333333333333",
        "task_name": "Inspect Project",
        "status_code": "PENDING",
    },
]


def _load_seed_data() -> dict:
    with SEED_DATA_PATH.open("r", encoding="utf-8") as seed_file:
        return json.load(seed_file)


def _find_seed_group(seed_data: dict, table_name: str) -> dict:
    for seed_group in seed_data["seedGroups"]:
        if seed_group["table"] == table_name:
            return seed_group

    raise AssertionError(f"Seed group not found for table: {table_name}")


def test_automation_factory_story1_seeds_core_platform_tasks():
    seed_data = _load_seed_data()
    task_seed_group = _find_seed_group(seed_data, "ccore_tasks")

    assert task_seed_group["conflictColumn"] == "task_id"
    assert task_seed_group["rows"] == EXPECTED_AUTOMATION_FACTORY_TASKS


def test_automation_factory_story1_rejects_old_demo_task_seeds():
    seed_data = _load_seed_data()
    task_seed_group = _find_seed_group(seed_data, "ccore_tasks")
    task_names = {row["task_name"] for row in task_seed_group["rows"]}

    assert "Workspace Bootstrap" not in task_names
    assert "Generate Project Structure" not in task_names
    assert "Execute Prefect Flow" not in task_names
