from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _cautomation_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir())


def _run_task_wrapper(cautomation_root: Path) -> subprocess.CompletedProcess[str]:
    script_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/validate_inputs/run_task.py"
    return subprocess.run([sys.executable, str(script_path)], cwd=cautomation_root.parent, text=True, capture_output=True, check=False)


def _runner_report_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/task_reports/validate_inputs_run_task_execution_report.json"


def _state_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/validate_inputs.json"


def test_validate_inputs_run_task_wrapper_executes_and_reports():
    cautomation_root = _cautomation_root()

    result = _run_task_wrapper(cautomation_root)

    assert result.returncode == 0
    report = json.loads(_runner_report_path(cautomation_root).read_text(encoding="utf-8"))
    assert report["status"] in {"PASSED", "PASSED_WITH_WARNINGS"}
    assert report["taskDefinitionId"] == "validate_inputs"
    assert report["reportType"] == "task_execution_report"
    state = json.loads(_state_path(cautomation_root).read_text(encoding="utf-8"))
    assert state["status"] in {"PASSED", "PASSED_WITH_WARNINGS"}
    assert state["gateDecision"] == "ACCEPTED"
