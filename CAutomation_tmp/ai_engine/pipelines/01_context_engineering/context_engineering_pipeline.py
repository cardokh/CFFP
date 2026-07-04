"""Pipeline 01 - Context Engineering orchestrator.

The pipeline is intentionally thin: it loads configuration, executes the configured
small task sequence, and writes an aggregate pipeline report. Business logic lives in
individual task folders under tasks/.

Run from the repository root:

    python CAutomation/ai_engine/pipelines/01_context_engineering/context_engineering_pipeline.py
"""

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
        self.task_registry_path = self._required_task_registry_path()
        self.task_registry = self._required_task_registry()
        self.task_definitions = self._required_task_definitions()
        self.task_instances = self._required_task_instances()
        self.state_root = self._resolve_project_path(self.output_config["pipelineStateRoot"])
        self.execution_id = self.timestamp
        self.archive_current_run = self.output_config.get("archiveCurrentRun", True) is True
        self.execution_history_root = self._optional_execution_history_root()
        self.archived_execution_root = (
            self.execution_history_root / self.execution_id
            if self.archive_current_run and self.execution_history_root is not None
            else None
        )

    def run(self) -> None:
        started = time.perf_counter()
        task_results: list[dict[str, Any]] = []
        final_status = "PASSED"
        self._prepare_state_root()
        try:
            for task_instance in self.task_instances:
                task_result = self._run_task(task_instance)
                task_results.append(task_result)
                if task_result["status"] == "FAILED" and task_instance.get("blocking", True) is True:
                    final_status = "FAILED"
                    break
                if task_result["status"] == "PASSED_WITH_WARNINGS" and final_status == "PASSED":
                    final_status = "PASSED_WITH_WARNINGS"

            # The final report task is responsible for the authoritative execution report.
            # If a blocking task failed before the final report task, try to run it anyway so
            # the current_run folder still contains an aggregate report.
            if final_status == "FAILED" and not any(result["taskDefinitionId"] == "write_execution_report" for result in task_results):
                final_task = next((task for task in self.task_instances if task.get("taskDefinitionId") == "write_execution_report"), None)
                if final_task is not None:
                    final_result = self._run_task(final_task)
                    task_results.append(final_result)

            final_status = self._read_final_task_status(final_status)
            report = self._build_pipeline_report(final_status, round(time.perf_counter() - started, 3), task_results)
            report_path = self.write_json_report(report)
            stable_report_path = self.state_root / "orchestrator_report.json"
            write_json_file(stable_report_path, report)
            self._archive_current_run()
            self._print_status(final_status, report_path)
        except Exception as exc:  # noqa: BLE001
            report = self._build_pipeline_report("FAILED", round(time.perf_counter() - started, 3), task_results)
            report["exceptionType"] = type(exc).__name__
            report["errors"] = [{"code": "unexpected_orchestrator_error", "message": str(exc)}]
            report_path = self.write_json_report(report)
            print_failed(f"{self.pipeline_id} FAILED; report {self.to_project_relative_path(report_path)}")
            raise

    def _run_task(self, task_instance: dict[str, Any]) -> dict[str, Any]:
        task_definition = self._task_definition_for_instance(task_instance)
        task_definition_id = task_definition["taskDefinitionId"]
        pipeline_task_id = task_instance["pipelineTaskId"]
        script_path = self.script_directory / task_definition["script"]
        started = time.perf_counter()
        environment = os.environ.copy()
        environment["CAUTOMATION_PIPELINE_TASK_INSTANCE"] = json.dumps(task_instance)
        environment["CAUTOMATION_PIPELINE_EXECUTION_ID"] = self.execution_id
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=self.project_root,
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        status = "PASSED" if completed.returncode == 0 else "FAILED"
        if completed.returncode == 0:
            print_passed(f"{task_definition_id} completed")
        else:
            print_failed(f"{task_definition_id} failed")
            if completed.stdout:
                print(completed.stdout.strip())
            if completed.stderr:
                print(completed.stderr.strip())
        return {
            "pipelineTaskId": pipeline_task_id,
            "taskDefinitionId": task_definition_id,
            "taskInstanceName": task_instance.get("taskInstanceName"),
            "script": task_definition["script"],
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
        if self.archive_current_run and self.execution_history_root is not None:
            self.execution_history_root.mkdir(parents=True, exist_ok=True)
            if self.archived_execution_root is not None and self.archived_execution_root.exists():
                shutil.rmtree(self.archived_execution_root)

    def _archive_current_run(self) -> None:
        if not self.archive_current_run or self.archived_execution_root is None:
            return
        if self.archived_execution_root.exists():
            shutil.rmtree(self.archived_execution_root)
        shutil.copytree(self.state_root, self.archived_execution_root)

    def _optional_execution_history_root(self) -> Path | None:
        configured = self.output_config.get("executionHistoryRoot")
        if not isinstance(configured, str) or not configured.strip():
            return None
        return self._resolve_project_path(configured)

    def _build_pipeline_report(self, status: str, elapsed_seconds: float, task_results: list[dict[str, Any]]) -> dict[str, Any]:
        report = {
            "scriptName": self.script_name,
            "pipelineId": self.pipeline_id,
            "pipelineVersion": self.pipeline_version,
            "executionId": self.execution_id,
            "status": status,
            "startedAtUtc": self.started_at_utc,
            "finishedAtUtc": self._utc_now_iso(),
            "elapsedSeconds": elapsed_seconds,
            "projectId": self.project_id,
            "moduleId": self.module_id,
            "taskRegistryPath": self.to_project_relative_path(self.task_registry_path),
            "taskResults": task_results,
            "stateRoot": self.to_project_relative_path(self.state_root),
            "currentRunRoot": self.to_project_relative_path(self.state_root),
        }
        if self.execution_history_root is not None:
            report["executionHistoryRoot"] = self.to_project_relative_path(self.execution_history_root)
        if self.archived_execution_root is not None:
            report["archivedExecutionRoot"] = self.to_project_relative_path(self.archived_execution_root)
        return report

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

    def _required_task_registry_path(self) -> Path:
        value = self.config.get("taskRegistryPath")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Config must contain non-empty string: taskRegistryPath")
        return self._resolve_project_path(value)

    def _required_task_registry(self) -> dict[str, Any]:
        if not self.task_registry_path.exists():
            raise FileNotFoundError(f"Task registry file does not exist: {self.task_registry_path}")
        registry = read_json_file(self.task_registry_path)
        if not isinstance(registry, dict):
            raise ValueError("Task registry must contain a JSON object.")
        return registry

    def _required_task_definitions(self) -> dict[str, dict[str, Any]]:
        value = self.task_registry.get("taskDefinitions")
        if not isinstance(value, list) or not value:
            raise ValueError("Task registry must contain a non-empty taskDefinitions array.")
        definitions: dict[str, dict[str, Any]] = {}
        for item in value:
            if not isinstance(item, dict):
                raise ValueError("Each task definition must be an object.")
            task_definition_id = item.get("taskDefinitionId")
            script = item.get("script")
            if not isinstance(task_definition_id, str) or not task_definition_id.strip():
                raise ValueError("Each task definition must contain taskDefinitionId.")
            if not isinstance(script, str) or not script.strip():
                raise ValueError(f"Task definition must contain script: {task_definition_id}")
            definitions[task_definition_id] = item
        return definitions

    def _required_task_instances(self) -> list[dict[str, Any]]:
        value = self.config.get("taskInstances")
        if not isinstance(value, list) or not value:
            raise ValueError("Config must contain a non-empty taskInstances array.")
        instances = sorted(value, key=lambda item: item.get("sequence", 0) if isinstance(item, dict) else 0)
        for item in instances:
            if not isinstance(item, dict):
                raise ValueError("Each task instance must be an object.")
            if not isinstance(item.get("pipelineTaskId"), str) or not item["pipelineTaskId"].strip():
                raise ValueError("Each task instance must contain pipelineTaskId.")
            if not isinstance(item.get("taskDefinitionId"), str) or not item["taskDefinitionId"].strip():
                raise ValueError("Each task instance must contain taskDefinitionId.")
            if item["taskDefinitionId"] not in self.task_definitions:
                raise ValueError(f"Task instance references unknown task definition: {item['taskDefinitionId']}")
        return instances

    def _task_definition_for_instance(self, task_instance: dict[str, Any]) -> dict[str, Any]:
        return self.task_definitions[task_instance["taskDefinitionId"]]

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
