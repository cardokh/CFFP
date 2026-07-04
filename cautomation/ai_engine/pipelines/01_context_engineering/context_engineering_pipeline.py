"""Pipeline 01 - Context Engineering orchestrator.

The pipeline is intentionally thin: it loads configuration, executes the configured
small task sequence, and writes an aggregate pipeline report. Business logic lives in
individual task folders under tasks/.

Run from the repository root:

    python cautomation/ai_engine/pipelines/01_context_engineering/context_engineering_pipeline.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _configure_project_import_path() -> Path:
    project_root = next(
        (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


_configure_project_import_path()

from scripts.shared.base_script import BaseScript  # noqa: E402
from scripts.shared.script_console_utils import print_failed, print_passed, print_warning  # noqa: E402
from scripts.shared.script_json_utils import read_json_file, write_json_file  # noqa: E402


class ContextEngineeringPipeline(BaseScript):
    """Orchestrates the configured Context Engineering task sequence."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.started_at_utc = self._utc_now_iso()
        self.pipeline_id = self._required_config_string("pipelineId")
        self.pipeline_version = self._required_config_string("pipelineVersion")
        self.project_id = self._required_config_string("projectId")
        self.module_id = self._required_config_string("moduleId")
        self.output_config = self._required_config_group("output")
        self.tasks = self._required_task_sequence()
        self.state_root = self._resolve_project_path(self.output_config["pipelineStateRoot"])

    def run(self) -> None:
        started = time.perf_counter()
        task_results: list[dict[str, Any]] = []
        final_status = "PASSED"
        self._prepare_state_root()
        try:
            for task in self.tasks:
                task_result = self._run_task(task)
                task_results.append(task_result)
                if task_result["status"] == "FAILED" and task.get("blocking", True) is True:
                    final_status = "FAILED"
                    break
                if task_result["status"] == "PASSED_WITH_WARNINGS" and final_status == "PASSED":
                    final_status = "PASSED_WITH_WARNINGS"

            # The final report task is responsible for the authoritative execution report.
            # If a blocking task failed before the final report task, try to run it anyway so
            # the current_run folder still contains an aggregate report.
            if final_status == "FAILED" and not any(result["taskId"] == "06_write_execution_report" for result in task_results):
                final_task = next((task for task in self.tasks if task.get("taskId") == "06_write_execution_report"), None)
                if final_task is not None:
                    final_result = self._run_task(final_task)
                    task_results.append(final_result)

            final_status = self._read_final_task_status(final_status)
            report = self._build_pipeline_report(final_status, round(time.perf_counter() - started, 3), task_results)
            report_path = self.write_json_report(report)
            stable_report_path = self.state_root / "orchestrator_report.json"
            write_json_file(stable_report_path, report)
            self._print_status(final_status, report_path)
        except Exception as exc:  # noqa: BLE001
            report = self._build_pipeline_report("FAILED", round(time.perf_counter() - started, 3), task_results)
            report["exceptionType"] = type(exc).__name__
            report["errors"] = [{"code": "unexpected_orchestrator_error", "message": str(exc)}]
            report_path = self.write_json_report(report)
            print_failed(f"{self.pipeline_id} FAILED; report {self.to_project_relative_path(report_path)}")
            raise

    def _run_task(self, task: dict[str, Any]) -> dict[str, Any]:
        task_id = task["taskId"]
        script_path = self.script_directory / task["script"]
        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=self.project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        status = "PASSED" if completed.returncode == 0 else "FAILED"
        if completed.returncode == 0:
            print_passed(f"{task_id} completed")
        else:
            print_failed(f"{task_id} failed")
            if completed.stdout:
                print(completed.stdout.strip())
            if completed.stderr:
                print(completed.stderr.strip())
        return {
            "taskId": task_id,
            "script": task["script"],
            "status": status,
            "returnCode": completed.returncode,
            "elapsedSeconds": round(time.perf_counter() - started, 3),
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }

    def _read_final_task_status(self, fallback_status: str) -> str:
        final_report_path = self.state_root / "pipeline_execution_report.json"
        if not final_report_path.exists():
            return fallback_status
        try:
            report = read_json_file(final_report_path)
        except Exception:  # noqa: BLE001 - fallback keeps orchestrator robust.
            return fallback_status
        status = report.get("status")
        if isinstance(status, str) and status.strip():
            return status
        return fallback_status

    def _prepare_state_root(self) -> None:
        if self.state_root.exists():
            shutil.rmtree(self.state_root)
        self.state_root.mkdir(parents=True, exist_ok=True)
        (self.state_root / "task_reports").mkdir(parents=True, exist_ok=True)

    def _build_pipeline_report(self, status: str, elapsed_seconds: float, task_results: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "scriptName": self.script_name,
            "pipelineId": self.pipeline_id,
            "pipelineVersion": self.pipeline_version,
            "status": status,
            "startedAtUtc": self.started_at_utc,
            "finishedAtUtc": self._utc_now_iso(),
            "elapsedSeconds": elapsed_seconds,
            "projectId": self.project_id,
            "moduleId": self.module_id,
            "taskResults": task_results,
            "stateRoot": self.to_project_relative_path(self.state_root),
        }

    def _print_status(self, status: str, report_path: Path) -> None:
        message = f"{self.pipeline_id} {status}; report {self.to_project_relative_path(report_path)}"
        if status == "PASSED":
            print_passed(message)
        elif status == "PASSED_WITH_WARNINGS":
            print_warning(message)
        else:
            print_failed(message)

    def _required_config_string(self, key: str) -> str:
        value = self.config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Config must contain non-empty string: {key}")
        return value

    def _required_config_group(self, key: str) -> dict[str, Any]:
        value = self.config.get(key)
        if not isinstance(value, dict):
            raise ValueError(f"Config must contain object: {key}")
        return value

    def _required_task_sequence(self) -> list[dict[str, Any]]:
        value = self.config.get("tasks")
        if not isinstance(value, list) or not value:
            raise ValueError("Config must contain a non-empty tasks array.")
        return value

    def _resolve_placeholders(self, value: str) -> str:
        replacements = {
            "projectId": self.project_id,
            "moduleId": self.module_id,
            "pipelineId": self.pipeline_id,
        }
        resolved = value
        for key, replacement in replacements.items():
            resolved = resolved.replace("{" + key + "}", replacement)
        return resolved

    def _resolve_project_path(self, configured_path: str) -> Path:
        path = Path(self._resolve_placeholders(configured_path))
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def _utc_now_iso(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    ContextEngineeringPipeline().run()
