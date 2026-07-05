"""Standard task execution entry point for Pipeline 01 tasks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _cautomation_root() -> Path:
    root = next((parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()), None)
    if root is None:
        raise RuntimeError("Could not locate CAutomation root containing scripts/shared.")
    return root


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_path(cautomation_root: Path, pipeline_config: dict[str, Any], value: str, execution_id: str) -> Path:
    replacements = {
        "projectId": str(pipeline_config.get("projectId", "")),
        "moduleId": str(pipeline_config.get("moduleId", "")),
        "pipelineId": str(pipeline_config.get("pipelineId", "")),
        "executionId": execution_id,
    }
    resolved = value
    for key, replacement in replacements.items():
        resolved = resolved.replace("{" + key + "}", replacement)
    path = Path(resolved)
    if not path.is_absolute():
        path = cautomation_root.parent / path
    return path.resolve()


def _status_from_completed_process(return_code: int, stdout: str, stderr: str) -> str:
    combined_output = f"{stdout}\n{stderr}"
    if return_code != 0:
        return "FAILED"
    if "PASSED_WITH_WARNINGS" in combined_output:
        return "PASSED_WITH_WARNINGS"
    return "PASSED"


def main() -> int:
    started = time.perf_counter()
    started_at = _utc_now_iso()
    task_dir = Path(__file__).resolve().parent
    task_definition_id = task_dir.name
    task_script = task_dir / f"{task_definition_id}.py"
    cautomation_root = _cautomation_root()
    task_config_path = task_dir / "config" / f"{task_definition_id}.json"
    execution_id = os.environ.get("CAUTOMATION_PIPELINE_EXECUTION_ID") or datetime.now().strftime("%Y%m%d_%H%M%S")
    pipeline_task_instance = os.environ.get("CAUTOMATION_PIPELINE_TASK_INSTANCE")

    report: dict[str, Any] = {
        "reportType": "task_execution_report",
        "runner": "run_task.py",
        "taskDefinitionId": task_definition_id,
        "executionId": execution_id,
        "startedAtUtc": started_at,
        "status": "FAILED",
    }

    try:
        task_config = _load_json(task_config_path)
        pipeline_config_path_value = task_config.get("pipelineConfigPath")
        if not isinstance(pipeline_config_path_value, str) or not pipeline_config_path_value.strip():
            raise ValueError("Task config must contain non-empty string: pipelineConfigPath")
        pipeline_config_path = Path(pipeline_config_path_value)
        if not pipeline_config_path.is_absolute():
            pipeline_config_path = cautomation_root.parent / pipeline_config_path
        pipeline_config = _load_json(pipeline_config_path.resolve())
        output_config = pipeline_config.get("output") if isinstance(pipeline_config.get("output"), dict) else {}
        reports_dir_value = output_config.get("taskReportsDirectory", "CAutomation/ai_engine/pipelines/01_context_engineering/output/current_run/task_reports")
        reports_dir = _resolve_path(cautomation_root, pipeline_config, str(reports_dir_value), execution_id)

        env = os.environ.copy()
        env["CAUTOMATION_PIPELINE_EXECUTION_ID"] = execution_id
        if pipeline_task_instance:
            env["CAUTOMATION_PIPELINE_TASK_INSTANCE"] = pipeline_task_instance

        completed = subprocess.run(
            [sys.executable, str(task_script)],
            cwd=cautomation_root.parent,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        status = _status_from_completed_process(completed.returncode, completed.stdout, completed.stderr)
        report.update({
            "pipelineId": pipeline_config.get("pipelineId"),
            "projectId": pipeline_config.get("projectId"),
            "moduleId": pipeline_config.get("moduleId"),
            "pipelineTaskInstance": json.loads(pipeline_task_instance) if pipeline_task_instance else None,
            "taskScript": str(task_script.relative_to(cautomation_root.parent)),
            "status": status,
            "returnCode": completed.returncode,
            "elapsedSeconds": round(time.perf_counter() - started, 3),
            "finishedAtUtc": _utc_now_iso(),
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        })
        report_path = reports_dir / f"{task_definition_id}_run_task_execution_report.json"
        report["reportPath"] = str(report_path.relative_to(cautomation_root.parent))
        _write_json(report_path, report)
        if completed.stdout:
            print(completed.stdout.strip())
        if completed.stderr:
            print(completed.stderr.strip(), file=sys.stderr)
        return completed.returncode
    except Exception as exc:  # noqa: BLE001
        report.update({
            "status": "FAILED",
            "exceptionType": type(exc).__name__,
            "errors": [{"code": "run_task_error", "message": str(exc)}],
            "elapsedSeconds": round(time.perf_counter() - started, 3),
            "finishedAtUtc": _utc_now_iso(),
        })
        fallback_path = task_dir / "output" / f"{task_definition_id}_run_task_execution_report.json"
        report["reportPath"] = str(fallback_path.relative_to(cautomation_root.parent))
        _write_json(fallback_path, report)
        print(f"{task_definition_id} FAILED; report {report['reportPath']}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
