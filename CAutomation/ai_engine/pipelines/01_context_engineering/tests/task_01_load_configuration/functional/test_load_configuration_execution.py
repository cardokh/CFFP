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


def test_load_configuration_runs_successfully_and_writes_state(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    repo_parent = cautomation_root.parent
    script_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/load_configuration/load_configuration.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=repo_parent,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    state_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/load_configuration.json"
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "PASSED"
    assert state["pipelineId"] == "01_context_engineering"
    assert state["projectId"] == "pipeline_management"
    assert state["moduleId"] == "pipeline_management"
    assert state["taskDefinitionCount"] == 6
    assert state["taskInstanceCount"] == 6
    assert state["errors"] == []
