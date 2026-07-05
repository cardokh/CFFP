"""Standard task test execution entry point for Pipeline 01 tasks."""

from __future__ import annotations

import json
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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _task_test_folder_name(task_dir: Path) -> str:
    sequence_by_task = {
        "load_configuration": "01",
        "validate_inputs": "02",
        "extract_contracts": "03",
        "build_context_package": "04",
        "validate_context_package": "05",
        "write_execution_report": "06",
    }
    task_definition_id = task_dir.name
    sequence = sequence_by_task.get(task_definition_id, "00")
    return f"task_{sequence}_{task_definition_id}"


def _run_pytest(cautomation_root: Path, test_path: Path, category: str) -> dict[str, Any]:
    started = time.perf_counter()
    if not test_path.exists():
        return {
            "category": category,
            "status": "NOT_FOUND",
            "returnCode": 1,
            "elapsedSeconds": 0.0,
            "testPath": str(test_path.relative_to(cautomation_root.parent)),
            "stdout": "",
            "stderr": f"Required {category} test folder does not exist.",
        }
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_path)],
        cwd=cautomation_root.parent,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "category": category,
        "status": "PASSED" if completed.returncode == 0 else "FAILED",
        "returnCode": completed.returncode,
        "elapsedSeconds": round(time.perf_counter() - started, 3),
        "testPath": str(test_path.relative_to(cautomation_root.parent)),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    started = time.perf_counter()
    task_dir = Path(__file__).resolve().parent
    task_definition_id = task_dir.name
    cautomation_root = _cautomation_root()
    pipeline_root = task_dir.parents[1]
    task_test_root = pipeline_root / "tests" / _task_test_folder_name(task_dir)
    category_results = [
        _run_pytest(cautomation_root, task_test_root / "unit", "unit"),
        _run_pytest(cautomation_root, task_test_root / "functional", "functional"),
        _run_pytest(cautomation_root, task_test_root / "validation", "validation"),
    ]
    status = "PASSED" if all(result["status"] == "PASSED" for result in category_results) else "FAILED"
    report_path = task_dir / "output" / f"{task_definition_id}_run_task_tests_report.json"
    report: dict[str, Any] = {
        "reportType": "task_test_report",
        "runner": "run_task_tests.py",
        "taskDefinitionId": task_definition_id,
        "status": status,
        "startedAtUtc": _utc_now_iso(),
        "finishedAtUtc": _utc_now_iso(),
        "elapsedSeconds": round(time.perf_counter() - started, 3),
        "testRoot": str(task_test_root.relative_to(cautomation_root.parent)),
        "categoryResults": category_results,
        "reportPath": str(report_path.relative_to(cautomation_root.parent)),
    }
    _write_json(report_path, report)
    print(f"{task_definition_id} tests {status}; report {report['reportPath']}")
    return 0 if status == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
