"""Standard pipeline execution entry point for Pipeline 01 - Context Engineering."""

from __future__ import annotations

import json
import os
import shutil
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


def _resolve_path(cautomation_root: Path, config: dict[str, Any], value: str, execution_id: str) -> Path:
    replacements = {
        "projectId": str(config.get("projectId", "")),
        "moduleId": str(config.get("moduleId", "")),
        "pipelineId": str(config.get("pipelineId", "")),
        "executionId": execution_id,
    }
    resolved = value
    for key, replacement in replacements.items():
        resolved = resolved.replace("{" + key + "}", replacement)
    path = Path(resolved)
    if not path.is_absolute():
        path = cautomation_root.parent / path
    return path.resolve()


def main() -> int:
    started = time.perf_counter()
    started_at = _utc_now_iso()
    pipeline_root = Path(__file__).resolve().parent
    cautomation_root = _cautomation_root()
    config = _load_json(pipeline_root / "config" / "context_engineering_pipeline.json")
    registry = _load_json(pipeline_root / "config" / "task_definitions.json")
    definitions = {item["taskDefinitionId"]: item for item in registry.get("taskDefinitions", []) if isinstance(item, dict) and "taskDefinitionId" in item}
    task_instances = sorted(config.get("taskInstances", []), key=lambda item: item.get("sequence", 0) if isinstance(item, dict) else 0)
    execution_id = os.environ.get("CAUTOMATION_PIPELINE_EXECUTION_ID") or datetime.now().strftime("%Y%m%d_%H%M%S")
    output_config = config.get("output") if isinstance(config.get("output"), dict) else {}
    state_root = _resolve_path(cautomation_root, config, str(output_config.get("pipelineStateRoot", "CAutomation/ai_engine/pipelines/01_context_engineering/output/current_run")), execution_id)
    history_root_value = output_config.get("executionHistoryRoot")
    archive_current_run = output_config.get("archiveCurrentRun", True) is True
    if state_root.exists():
        shutil.rmtree(state_root)
    (state_root / "task_reports").mkdir(parents=True, exist_ok=True)

    task_results: list[dict[str, Any]] = []
    final_status = "PASSED"
    for task_instance in task_instances:
        task_definition_id = task_instance.get("taskDefinitionId")
        definition = definitions.get(task_definition_id)
        if definition is None:
            result = {
                "taskDefinitionId": task_definition_id,
                "pipelineTaskId": task_instance.get("pipelineTaskId"),
                "status": "FAILED",
                "returnCode": 1,
                "errors": [{"code": "unknown_task_definition", "message": f"Unknown task definition: {task_definition_id}"}],
            }
            task_results.append(result)
            final_status = "FAILED"
            break
        task_script = pipeline_root / str(definition["script"])
        run_task = task_script.parent / "run_task.py"
        task_started = time.perf_counter()
        env = os.environ.copy()
        env["CAUTOMATION_PIPELINE_EXECUTION_ID"] = execution_id
        env["CAUTOMATION_PIPELINE_TASK_INSTANCE"] = json.dumps(task_instance)
        completed = subprocess.run([sys.executable, str(run_task)], cwd=cautomation_root.parent, text=True, capture_output=True, check=False, env=env)
        combined_output = completed.stdout + "\n" + completed.stderr
        status = "FAILED" if completed.returncode != 0 else ("PASSED_WITH_WARNINGS" if "PASSED_WITH_WARNINGS" in combined_output else "PASSED")
        result = {
            "pipelineTaskId": task_instance.get("pipelineTaskId"),
            "taskDefinitionId": task_definition_id,
            "taskInstanceName": task_instance.get("taskInstanceName"),
            "runner": str(run_task.relative_to(cautomation_root.parent)),
            "status": status,
            "returnCode": completed.returncode,
            "elapsedSeconds": round(time.perf_counter() - task_started, 3),
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
        task_results.append(result)
        if status == "FAILED" and task_instance.get("blocking", True) is True:
            final_status = "FAILED"
            break
        if status == "PASSED_WITH_WARNINGS" and final_status == "PASSED":
            final_status = "PASSED_WITH_WARNINGS"

    report_path = state_root / "pipeline_execution_report.json"
    report: dict[str, Any] = {
        "reportType": "pipeline_execution_report",
        "runner": "run_pipeline.py",
        "pipelineId": config.get("pipelineId"),
        "pipelineVersion": config.get("pipelineVersion"),
        "projectId": config.get("projectId"),
        "moduleId": config.get("moduleId"),
        "executionId": execution_id,
        "status": final_status,
        "startedAtUtc": started_at,
        "finishedAtUtc": _utc_now_iso(),
        "elapsedSeconds": round(time.perf_counter() - started, 3),
        "taskResults": task_results,
        "reportPath": str(report_path.relative_to(cautomation_root.parent)),
    }
    _write_json(report_path, report)
    final_report_dir = _resolve_path(cautomation_root, config, str(output_config.get("finalReportDirectory", "CAutomation/ai_engine/pipelines/01_context_engineering/output")), execution_id)
    timestamped_report = final_report_dir / f"run_pipeline_{execution_id}.json"
    _write_json(timestamped_report, report)
    if archive_current_run and isinstance(history_root_value, str) and history_root_value.strip():
        history_root = _resolve_path(cautomation_root, config, history_root_value, execution_id)
        archived_root = history_root / execution_id
        if archived_root.exists():
            shutil.rmtree(archived_root)
        shutil.copytree(state_root, archived_root)
        report["archivedExecutionRoot"] = str(archived_root.relative_to(cautomation_root.parent))
    print(f"{config.get('pipelineId')} {final_status}; report {report['reportPath']}")
    return 1 if final_status == "FAILED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
