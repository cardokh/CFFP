from pathlib import Path


def test_task_runner_exists():
    runner = Path("CAutomation/ai_engine/pipelines/01_context_engineering/tasks/write_execution_report/run_task.py")
    assert runner.exists()
