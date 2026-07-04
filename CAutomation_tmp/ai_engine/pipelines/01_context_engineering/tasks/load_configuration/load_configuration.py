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
            self.write_state_json(self.current_task_state_file(), state_payload)
            report = self.base_report(status, started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"summary": state_payload})
            report_path = self.write_task_report(report)
            if status == "FAILED":
                print_failed(f"load_configuration FAILED; report {self.to_project_relative_path(report_path)}")
            else:
                print_passed(f"load_configuration PASSED; report {self.to_project_relative_path(report_path)}")
        except Exception as exc:  # noqa: BLE001
            report = self.base_report("FAILED", started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"errors": [{"code": "unexpected_error", "message": str(exc)}], "exceptionType": type(exc).__name__})
            report_path = self.write_task_report(report)
            print_failed(f"load_configuration FAILED; report {self.to_project_relative_path(report_path)}")
            raise


if __name__ == "__main__":
    LoadConfigurationTask().run()
