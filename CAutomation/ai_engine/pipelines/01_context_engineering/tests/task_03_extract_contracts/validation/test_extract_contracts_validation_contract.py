from pathlib import Path


def test_task_config_exists():
    config = Path("CAutomation/ai_engine/pipelines/01_context_engineering/tasks/extract_contracts/config/extract_contracts.json")
    assert config.exists()
