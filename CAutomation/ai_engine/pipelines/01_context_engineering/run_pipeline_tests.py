"""Standard pipeline test execution entry point for Pipeline 01 - Context Engineering."""

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


def main() -> int:
    started = time.perf_counter()
    pipeline_root = Path(__file__).resolve().parent
    cautomation_root = _cautomation_root()
    config = _load_json(pipeline_root / "config" / "context_engineering_pipeline.json")
    registry = _load_json(pipeline_root / "config" / "task_definitions.json")
    definitions = {item["taskDefinitionId"]: item for item in registry.get("taskDefinitions", []) if isinstance(item, dict) and "taskDefinitionId" in item}
    task_instances = sorted(config.get("taskInstances", []), key=lambda item: item.get("sequence", 0) if isinstance(item, dict) else 0)
    task_test_results: list[dict[str, Any]] = []
    for task_instance in task_instances:
        task_definition_id = task_instance.get("taskDefinitionId")
        definition = definitions.get(task_definition_id)
        task_started = time.perf_counter()
        if definition is None:
            task_test_results.append({"taskDefinitionId": task_definition_id, "status": "FAILED", "returnCode": 1})
            continue
        task_script = pipeline_root / str(definition["script"])
        runner = task_script.parent / "run_task_tests.py"
        env = os.environ.copy()
        env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
        completed = subprocess.run([sys.executable, str(runner)], cwd=cautomation_root.parent, text=True, capture_output=True, check=False, env=env)
        task_test_results.append({
            "pipelineTaskId": task_instance.get("pipelineTaskId"),
            "taskDefinitionId": task_definition_id,
            "taskInstanceName": task_instance.get("taskInstanceName"),
            "runner": str(runner.relative_to(cautomation_root.parent)),
            "status": "PASSED" if completed.returncode == 0 else "FAILED",
            "returnCode": completed.returncode,
            "elapsedSeconds": round(time.perf_counter() - task_started, 3),
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        })
    status = "PASSED" if all(result["status"] == "PASSED" for result in task_test_results) else "FAILED"
    report_path = pipeline_root / "output" / "pipeline_test_report.json"
    report: dict[str, Any] = {
        "reportType": "pipeline_test_report",
        "runner": "run_pipeline_tests.py",
        "pipelineId": config.get("pipelineId"),
        "pipelineVersion": config.get("pipelineVersion"),
        "projectId": config.get("projectId"),
        "moduleId": config.get("moduleId"),
        "status": status,
        "startedAtUtc": _utc_now_iso(),
        "finishedAtUtc": _utc_now_iso(),
        "elapsedSeconds": round(time.perf_counter() - started, 3),
        "taskTestResults": task_test_results,
        "reportPath": str(report_path.relative_to(cautomation_root.parent)),
    }
    _write_json(report_path, report)
    print(f"{config.get('pipelineId')} tests {status}; report {report['reportPath']}")
    return 0 if status == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
