"""Task 06 - Write Execution Report for Pipeline 01 Context Engineering."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

_TASKS_ROOT = Path(__file__).resolve().parents[1]
if str(_TASKS_ROOT) not in sys.path:
    sys.path.insert(0, str(_TASKS_ROOT))

from _shared.context_engineering_common import ContextEngineeringSupportMixin, configure_project_import_path, utc_now_iso  # noqa: E402

configure_project_import_path(__file__)

from scripts.shared.base_script import BaseScript  # noqa: E402
from scripts.shared.script_console_utils import print_failed, print_passed, print_warning  # noqa: E402
from scripts.shared.script_json_utils import read_json_file, write_json_file  # noqa: E402


class WriteExecutionReportTask(ContextEngineeringSupportMixin, BaseScript):
    """Aggregates Pipeline 01 state into the final execution report."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.pipeline_config: dict[str, Any] = self.load_pipeline_config()

    def run(self) -> None:
        started = time.perf_counter()
        started_at_utc = utc_now_iso()
        warnings: list[dict[str, str]] = []
        errors: list[dict[str, str]] = []
        task_states: list[dict[str, Any]] = []
        try:
            current_task_id = self.task_id()
            state_files = [
                task["stateFile"]
                for task in sorted(self.pipeline_config.get("tasks", []), key=lambda item: item.get("sequence", 0))
                if isinstance(task, dict)
                and task.get("taskId") != current_task_id
                and isinstance(task.get("stateFile"), str)
            ]
            for file_name in state_files:
                path = self.state_file(file_name)
                if not path.exists():
                    errors.append({"code": "missing_task_state", "message": f"Missing task state file: {path}"})
                    continue
                state = read_json_file(path)
                task_states.append({"stateFile": self.to_project_relative_path(path), "state": state})
                warnings.extend(state.get("warnings", []))
                errors.extend(state.get("errors", []))

            build_state = next((item["state"] for item in task_states if item["stateFile"].endswith(self.pipeline_task_state_file("build_context_package"))), {})
            validation_state = next((item["state"] for item in task_states if item["stateFile"].endswith(self.pipeline_task_state_file("validate_context_package"))), {})
            package_dir = build_state.get("contextPackageDirectory", self.to_project_relative_path(self.context_package_dir()))
            warnings = self._unique_messages(warnings)
            errors = self._unique_messages(errors)
            status = self.status_from(warnings, errors)
            final_report = {
                "pipelineId": self.pipeline_id(),
                "pipelineName": self.pipeline_config.get("pipelineName"),
                "pipelineVersion": self.pipeline_config.get("pipelineVersion"),
                "status": status,
                "startedAtUtc": started_at_utc,
                "finishedAtUtc": utc_now_iso(),
                "elapsedSeconds": round(time.perf_counter() - started, 3),
                "projectId": self.project_id(),
                "moduleId": self.module_id(),
                "contextPackageDirectory": package_dir,
                "summary": {
                    "configuredTaskCount": len(self.pipeline_config.get("tasks", [])) if isinstance(self.pipeline_config.get("tasks"), list) else 0,
                    "aggregatedTaskStateCount": len(task_states),
                    "generatedFileCount": len(build_state.get("generatedFiles", [])) if isinstance(build_state, dict) else 0,
                    "warningCount": len(warnings),
                    "errorCount": len(errors),
                },
                "taskStates": task_states,
                "contextPackageValidation": validation_state,
                "warnings": warnings,
                "errors": errors,
            }
            final_report_path = self.write_json_report(final_report)
            self.write_state_json(self.current_task_state_file(), {"status": status, "finalReportPath": self.to_project_relative_path(final_report_path)})
            # Also write a stable report name for humans and downstream tools.
            stable_path = self.state_root() / "pipeline_execution_report.json"
            write_json_file(stable_path, final_report)
            report = self.base_report(status, started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"summary": final_report["summary"], "finalReportPath": self.to_project_relative_path(final_report_path)})
            task_report_path = self.write_task_report(report)
            if status == "FAILED":
                print_failed(f"write_execution_report FAILED; report {self.to_project_relative_path(task_report_path)}; final {self.to_project_relative_path(final_report_path)}")
            elif status == "PASSED_WITH_WARNINGS":
                print_warning(f"write_execution_report PASSED_WITH_WARNINGS; report {self.to_project_relative_path(task_report_path)}; final {self.to_project_relative_path(final_report_path)}")
            else:
                print_passed(f"write_execution_report PASSED; report {self.to_project_relative_path(task_report_path)}; final {self.to_project_relative_path(final_report_path)}")
        except Exception as exc:  # noqa: BLE001
            report = self.base_report("FAILED", started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"errors": [{"code": "unexpected_error", "message": str(exc)}], "exceptionType": type(exc).__name__})
            report_path = self.write_task_report(report)
            print_failed(f"write_execution_report FAILED; report {self.to_project_relative_path(report_path)}")
            raise

    def _unique_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        unique: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for message in messages:
            key = (str(message.get("code", "")), str(message.get("message", "")))
            if key not in seen:
                seen.add(key)
                unique.append(message)
        return unique


if __name__ == "__main__":
    WriteExecutionReportTask().run()
