from pathlib import Path


def test_task_config_exists():
    config = Path("CAutomation/ai_engine/pipelines/01_context_engineering/tasks/write_execution_report/config/write_execution_report.json")
    assert config.exists()
