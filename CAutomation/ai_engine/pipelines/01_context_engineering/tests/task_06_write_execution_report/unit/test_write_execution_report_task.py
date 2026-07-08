import importlib.util
from pathlib import Path


def test_task_class_exists():
    module_path = Path("CAutomation/ai_engine/pipelines/01_context_engineering/tasks/write_execution_report/write_execution_report.py")
    spec = importlib.util.spec_from_file_location("write_execution_report", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert getattr(module, "WriteExecutionReportTask").__name__ == "WriteExecutionReportTask"
