from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _cautomation_root() -> Path:
    return next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "scripts" / "shared").is_dir()
    )


def _load_task_class():
    cautomation_root = _cautomation_root()
    for import_root in (cautomation_root, cautomation_root.parent):
        if str(import_root) not in sys.path:
            sys.path.insert(0, str(import_root))
    module_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/load_configuration/load_configuration.py"
    spec = importlib.util.spec_from_file_location("load_configuration_task", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LoadConfigurationTask


def test_load_configuration_loads_pipeline_config_and_task_registry(monkeypatch):
    cautomation_root = _cautomation_root()
    monkeypatch.chdir(cautomation_root.parent)

    task = _load_task_class()()

    assert task.pipeline_config["pipelineId"] == "01_context_engineering"
    assert task.pipeline_config["projectId"] == "CAutomation"
    assert task.pipeline_config["moduleId"] == "pipeline_management"
    assert task.task_registry["taskDefinitions"]
    assert len(task.task_registry["taskDefinitions"]) == 6


def test_load_configuration_resolves_config_paths_from_repository_root(monkeypatch):
    cautomation_root = _cautomation_root()
    monkeypatch.chdir(cautomation_root.parent)

    task = _load_task_class()()

    assert task.pipeline_config_path.exists()
    assert task.task_registry_path.exists()
    assert task.to_project_relative_path(task.pipeline_config_path).endswith(
        "CAutomation/ai_engine/pipelines/01_context_engineering/config/context_engineering_pipeline.json"
    )
