from pathlib import Path


def test_task_runner_exists():
    runner = Path("CAutomation/ai_engine/pipelines/01_context_engineering/tasks/validate_context_package/run_task.py")
    assert runner.exists()
