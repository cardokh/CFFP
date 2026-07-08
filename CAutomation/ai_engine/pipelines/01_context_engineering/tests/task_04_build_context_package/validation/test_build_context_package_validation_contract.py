from pathlib import Path


def test_task_config_exists():
    config = Path("CAutomation/ai_engine/pipelines/01_context_engineering/tasks/build_context_package/config/build_context_package.json")
    assert config.exists()
