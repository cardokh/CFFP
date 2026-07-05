"""Task 01 - Load Configuration for Pipeline 01 Context Engineering."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

_TASKS_ROOT = Path(__file__).resolve().parents[1]
if str(_TASKS_ROOT) not in sys.path:
    sys.path.insert(0, str(_TASKS_ROOT))

from _shared.context_engineering_common import (  # noqa: E402
    ContextEngineeringSupportMixin,
    configure_project_import_path,
    utc_now_iso,
)

configure_project_import_path(__file__)

from scripts.shared.base_script import BaseScript  # noqa: E402
from scripts.shared.script_console_utils import print_failed, print_passed  # noqa: E402


class LoadConfigurationTask(ContextEngineeringSupportMixin, BaseScript):
    """Loads and validates the pipeline-level JSON configuration."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.pipeline_config: dict[str, Any] = self.load_pipeline_config()
        self.task_registry: dict[str, Any] = self.load_task_registry()

    def load_task_registry(self) -> dict[str, Any]:
        """Loads the task registry without requiring the pipeline config to be fully valid first."""
        from scripts.shared.script_json_utils import read_json_file

        configured_path = self.pipeline_config.get("taskRegistryPath")
        if not isinstance(configured_path, str) or not configured_path.strip():
            self.task_registry_path = self.project_root.resolve()
            return {}
        resolved_path = configured_path
        for key in ("projectId", "moduleId", "pipelineId"):
            value = self.pipeline_config.get(key)
            if isinstance(value, str):
                resolved_path = resolved_path.replace("{" + key + "}", value)
        path = Path(resolved_path)
        if not path.is_absolute():
            path = self.project_root / path
        self.task_registry_path = path.resolve()
        registry = read_json_file(path)
        if not isinstance(registry, dict):
            raise ValueError(f"Task registry must contain a JSON object: {path}")
        return registry

    def load_configuration_state_file(self) -> str:
        """Returns the Task 01 state file without trusting the config being validated."""
        for task_instance in self.pipeline_config.get("taskInstances", []):
            if not isinstance(task_instance, dict):
                continue
            if (
                task_instance.get("pipelineTaskId") == "context_engineering.load_configuration"
                or task_instance.get("taskDefinitionId") == "load_configuration"
            ):
                state_file = task_instance.get("stateFile")
                if isinstance(state_file, str) and state_file.strip():
                    return state_file
        return "load_configuration.json"

    def resolve_load_configuration_path(self, configured_path: str) -> Path:
        """Resolves Task 01 output paths without requiring a valid pipeline contract."""
        resolved_path = configured_path
        for key in ("projectId", "moduleId", "pipelineId"):
            value = self.pipeline_config.get(key)
            if isinstance(value, str):
                resolved_path = resolved_path.replace("{" + key + "}", value)
        path = Path(resolved_path)
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def write_load_configuration_state_json(self, file_name: str, payload: dict[str, Any]) -> Path:
        """Writes Task 01 state without depending on validated runtime helpers."""
        from scripts.shared.script_json_utils import write_json_file

        output_config = self.pipeline_config.get("output")
        if not isinstance(output_config, dict):
            output_config = {}
        state_root_value = output_config.get("pipelineStateRoot")
        if not isinstance(state_root_value, str) or not state_root_value.strip():
            state_root_value = "CAutomation/ai_engine/pipelines/01_context_engineering/output/current_run"
        path = self.resolve_load_configuration_path(state_root_value) / file_name
        write_json_file(path, payload)
        return path

    def write_load_configuration_task_report(self, report: dict[str, Any]) -> Path:
        """Writes Task 01 reports without depending on validated runtime helpers."""
        from scripts.shared.script_json_utils import write_json_file

        report_path = self.write_json_report(report)
        output_config = self.pipeline_config.get("output")
        if isinstance(output_config, dict):
            reports_dir_value = output_config.get("taskReportsDirectory")
            if isinstance(reports_dir_value, str) and reports_dir_value.strip():
                copied_report_path = self.resolve_load_configuration_path(reports_dir_value) / report_path.name
                write_json_file(copied_report_path, report)
        return report_path

    def load_configuration_report(self, status: str, started_at_utc: str, elapsed_seconds: float) -> dict[str, Any]:
        """Builds a Task 01 report without requiring validated config values."""
        return {
            "scriptName": self.script_name,
            "pipelineId": self.pipeline_config.get("pipelineId"),
            "executionId": self.pipeline_execution_id(),
            "pipelineTaskId": "context_engineering.load_configuration",
            "taskDefinitionId": "load_configuration",
            "taskId": "load_configuration",
            "taskVersion": self.config.get("taskVersion"),
            "status": status,
            "startedAtUtc": started_at_utc,
            "finishedAtUtc": utc_now_iso(),
            "elapsedSeconds": elapsed_seconds,
            "configuration": {
                "taskConfigPath": self.to_project_relative_path(self.config_path),
                "pipelineConfigPath": self.to_project_relative_path(self.pipeline_config_path),
                "projectId": self.pipeline_config.get("projectId"),
                "moduleId": self.pipeline_config.get("moduleId"),
                "pipelineTaskId": "context_engineering.load_configuration",
                "taskDefinitionId": "load_configuration",
            },
        }

    def run(self) -> None:
        started = time.perf_counter()
        started_at_utc = utc_now_iso()
        errors: list[dict[str, str]] = []
        warnings: list[dict[str, str]] = []
        try:
            required_groups = ["input", "output", "contextFiles", "structuredFiles", "validation"]
            for group_name in required_groups:
                if not isinstance(self.pipeline_config.get(group_name), dict):
                    errors.append({"code": "missing_config_group", "message": f"Missing config group: {group_name}"})
            required_strings = ["pipelineId", "projectId", "moduleId", "pipelineVersion", "taskRegistryPath"]
            for key in required_strings:
                if not isinstance(self.pipeline_config.get(key), str) or not self.pipeline_config[key].strip():
                    errors.append({"code": "missing_config_value", "message": f"Missing config value: {key}"})
            task_definitions = self.task_registry.get("taskDefinitions")
            if not isinstance(task_definitions, list) or not task_definitions:
                errors.append({"code": "missing_task_definitions", "message": "Task registry must define a non-empty taskDefinitions array."})
            if not isinstance(self.pipeline_config.get("taskInstances"), list) or not self.pipeline_config["taskInstances"]:
                errors.append({"code": "missing_task_instances", "message": "Pipeline config must define a non-empty taskInstances array."})
            definition_ids = {
                item.get("taskDefinitionId")
                for item in task_definitions or []
                if isinstance(item, dict)
            }
            for task_instance in self.pipeline_config.get("taskInstances", []):
                if not isinstance(task_instance, dict):
                    errors.append({"code": "invalid_task_instance", "message": "Each task instance must be an object."})
                    continue
                if task_instance.get("taskDefinitionId") not in definition_ids:
                    errors.append({"code": "unknown_task_definition", "message": f"Task instance references unknown task definition: {task_instance.get('taskDefinitionId')}"})

            status = self.status_from(warnings, errors)
            state_payload = {
                "status": status,
                "pipelineConfigPath": self.to_project_relative_path(self.pipeline_config_path),
                "taskRegistryPath": self.to_project_relative_path(self.task_registry_path),
                "pipelineId": self.pipeline_config.get("pipelineId"),
                "projectId": self.pipeline_config.get("projectId"),
                "moduleId": self.pipeline_config.get("moduleId"),
                "taskDefinitionCount": len(task_definitions) if isinstance(task_definitions, list) else 0,
                "taskInstanceCount": len(self.pipeline_config.get("taskInstances", [])) if isinstance(self.pipeline_config.get("taskInstances"), list) else 0,
                "warnings": warnings,
                "errors": errors,
            }
            self.write_load_configuration_state_json(self.load_configuration_state_file(), state_payload)
            report = self.load_configuration_report(status, started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"summary": state_payload})
            report_path = self.write_load_configuration_task_report(report)
            if status == "FAILED":
                print_failed(f"load_configuration FAILED; report {self.to_project_relative_path(report_path)}")
            else:
                print_passed(f"load_configuration PASSED; report {self.to_project_relative_path(report_path)}")
        except Exception as exc:  # noqa: BLE001
            report = self.load_configuration_report("FAILED", started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"errors": [{"code": "unexpected_error", "message": str(exc)}], "exceptionType": type(exc).__name__})
            report_path = self.write_load_configuration_task_report(report)
            print_failed(f"load_configuration FAILED; report {self.to_project_relative_path(report_path)}")
            raise


if __name__ == "__main__":
    LoadConfigurationTask().run()
