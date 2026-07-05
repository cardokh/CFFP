from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def _cautomation_root() -> Path:
    return next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "scripts" / "shared").is_dir()
    )


def _copy_repo(tmp_path: Path) -> Path:
    source_root = _cautomation_root()
    target_root = tmp_path / "CAutomation"
    ignore = shutil.ignore_patterns("__pycache__", ".pytest_cache", "output")
    shutil.copytree(source_root, target_root, ignore=ignore)
    return target_root


def _run_task(cautomation_root: Path) -> subprocess.CompletedProcess[str]:
    script_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/load_configuration/load_configuration.py"
    return subprocess.run(
        [sys.executable, str(script_path)],
        cwd=cautomation_root.parent,
        text=True,
        capture_output=True,
        check=False,
    )


def _pipeline_config_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/config/context_engineering_pipeline.json"


def test_load_configuration_rejects_missing_required_pipeline_value(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config_path = _pipeline_config_path(cautomation_root)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["projectId"] = ""
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    state_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/load_configuration.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "FAILED"
    assert {error["code"] for error in state["errors"]} == {"missing_config_value"}


def test_load_configuration_rejects_unknown_task_definition_reference(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config_path = _pipeline_config_path(cautomation_root)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["taskInstances"][0]["taskDefinitionId"] = "does_not_exist"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    state_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/load_configuration.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "FAILED"
    assert {error["code"] for error in state["errors"]} == {"unknown_task_definition"}
