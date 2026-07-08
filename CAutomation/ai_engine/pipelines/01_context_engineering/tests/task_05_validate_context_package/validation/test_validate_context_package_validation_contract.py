from pathlib import Path


def test_task_config_exists():
    config = Path("CAutomation/ai_engine/pipelines/01_context_engineering/tasks/validate_context_package/config/validate_context_package.json")
    assert config.exists()
