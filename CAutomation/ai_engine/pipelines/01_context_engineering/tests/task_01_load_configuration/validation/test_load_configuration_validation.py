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


def _run_task_wrapper(cautomation_root: Path) -> subprocess.CompletedProcess[str]:
    script_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/load_configuration/run_task.py"
    return subprocess.run(
        [sys.executable, str(script_path)],
        cwd=cautomation_root.parent,
        text=True,
        capture_output=True,
        check=False,
    )


def _pipeline_config_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/config/context_engineering_pipeline.json"


def _task_registry_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/config/task_definitions.json"


def _state_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/load_configuration.json"


def _task_report_path(cautomation_root: Path) -> Path:
    task_reports_dir = cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/task_reports"
    matches = sorted(task_reports_dir.glob("load_configuration_*.json"))
    assert matches, f"No load_configuration task report found in {task_reports_dir}"
    return matches[-1]


def _runner_report_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/task_reports/load_configuration_run_task_execution_report.json"


def _write_pipeline_config(cautomation_root: Path, config: dict) -> None:
    _pipeline_config_path(cautomation_root).write_text(json.dumps(config, indent=2), encoding="utf-8")


def _read_pipeline_config(cautomation_root: Path) -> dict:
    return json.loads(_pipeline_config_path(cautomation_root).read_text(encoding="utf-8"))


def _read_state(cautomation_root: Path) -> dict:
    return json.loads(_state_path(cautomation_root).read_text(encoding="utf-8"))


def _assert_failed_state_with_codes(cautomation_root: Path, expected_codes: set[str]) -> None:
    state = _read_state(cautomation_root)
    assert state["status"] == "FAILED"
    assert {error["code"] for error in state["errors"]} == expected_codes


def test_load_configuration_rejects_missing_required_pipeline_value(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config = _read_pipeline_config(cautomation_root)
    config["projectId"] = ""
    _write_pipeline_config(cautomation_root, config)

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    _assert_failed_state_with_codes(cautomation_root, {"missing_config_value"})


def test_load_configuration_rejects_unknown_task_definition_reference(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config = _read_pipeline_config(cautomation_root)
    config["taskInstances"][0]["taskDefinitionId"] = "does_not_exist"
    _write_pipeline_config(cautomation_root, config)

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    _assert_failed_state_with_codes(cautomation_root, {"unknown_task_definition"})


def test_load_configuration_rejects_missing_required_config_group(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config = _read_pipeline_config(cautomation_root)
    del config["validation"]
    _write_pipeline_config(cautomation_root, config)

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    _assert_failed_state_with_codes(cautomation_root, {"missing_config_group"})


def test_load_configuration_rejects_empty_task_registry(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    registry = json.loads(_task_registry_path(cautomation_root).read_text(encoding="utf-8"))
    registry["taskDefinitions"] = []
    _task_registry_path(cautomation_root).write_text(json.dumps(registry, indent=2), encoding="utf-8")

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    _assert_failed_state_with_codes(cautomation_root, {"missing_task_definitions", "unknown_task_definition"})


def test_load_configuration_rejects_missing_task_instances(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config = _read_pipeline_config(cautomation_root)
    config["taskInstances"] = []
    _write_pipeline_config(cautomation_root, config)

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    _assert_failed_state_with_codes(cautomation_root, {"missing_task_instances"})


def test_load_configuration_rejects_invalid_task_instance_object(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config = _read_pipeline_config(cautomation_root)
    config["taskInstances"][0] = "not-an-object"
    _write_pipeline_config(cautomation_root, config)

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    _assert_failed_state_with_codes(cautomation_root, {"invalid_task_instance"})


def test_load_configuration_rejects_missing_task_registry_path_value(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config = _read_pipeline_config(cautomation_root)
    config["taskRegistryPath"] = ""
    _write_pipeline_config(cautomation_root, config)

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    _assert_failed_state_with_codes(cautomation_root, {"missing_config_value", "missing_task_definitions", "unknown_task_definition"})


def test_load_configuration_report_contains_required_execution_fields(tmp_path):
    cautomation_root = _copy_repo(tmp_path)

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    report = json.loads(_task_report_path(cautomation_root).read_text(encoding="utf-8"))
    for key in (
        "scriptName",
        "pipelineId",
        "executionId",
        "pipelineTaskId",
        "taskDefinitionId",
        "taskId",
        "taskVersion",
        "status",
        "startedAtUtc",
        "finishedAtUtc",
        "elapsedSeconds",
        "configuration",
        "summary",
    ):
        assert key in report
    assert report["status"] == "PASSED"
    assert report["summary"]["status"] == "PASSED"
    assert report["summary"]["errors"] == []


def test_run_task_wrapper_reports_missing_pipeline_config_file(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    _pipeline_config_path(cautomation_root).unlink()

    result = _run_task_wrapper(cautomation_root)

    assert result.returncode == 1
    report = json.loads(
        (cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/load_configuration/output/load_configuration_run_task_execution_report.json")
        .read_text(encoding="utf-8")
    )
    assert report["status"] == "FAILED"
    assert report["exceptionType"] == "FileNotFoundError"
    assert report["errors"][0]["code"] == "run_task_error"


def test_run_task_wrapper_reports_malformed_pipeline_config_file(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    _pipeline_config_path(cautomation_root).write_text("{ not valid json", encoding="utf-8")

    result = _run_task_wrapper(cautomation_root)

    assert result.returncode == 1
    report = json.loads(
        (cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/load_configuration/output/load_configuration_run_task_execution_report.json")
        .read_text(encoding="utf-8")
    )
    assert report["status"] == "FAILED"
    assert report["exceptionType"] == "JSONDecodeError"
    assert report["errors"][0]["code"] == "run_task_error"
