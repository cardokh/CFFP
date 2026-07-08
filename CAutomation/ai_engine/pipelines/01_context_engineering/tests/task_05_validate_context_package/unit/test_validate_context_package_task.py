import importlib.util
from pathlib import Path


def test_task_class_exists():
    module_path = Path("CAutomation/ai_engine/pipelines/01_context_engineering/tasks/validate_context_package/validate_context_package.py")
    spec = importlib.util.spec_from_file_location("validate_context_package", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert getattr(module, "ValidateContextPackageTask").__name__ == "ValidateContextPackageTask"
