"""Task 02 - Validate Inputs for Pipeline 01 Context Engineering."""

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


class ValidateInputsTask(ContextEngineeringSupportMixin, BaseScript):
    """Validates required project and module input contracts."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.pipeline_config: dict[str, Any] = self.load_pipeline_config()

    def run(self) -> None:
        started = time.perf_counter()
        started_at_utc = utc_now_iso()
        checks: list[dict[str, Any]] = []
        warnings: list[dict[str, str]] = []
        errors: list[dict[str, str]] = []
        try:
            srs_path, ats_path = self.contract_paths()
            required_paths = {
                "cautomation_root_exists": self.cautomation_root(),
                "project_config_exists": self.project_config_path(),
                "module_input_root_exists": self.module_input_root(),
                "module_srs_exists": srs_path,
                "module_ats_exists": ats_path,
            }
            for name, path in required_paths.items():
                passed = path.exists()
                checks.append({
                    "name": name,
                    "path": self.to_project_relative_path(path) if path.exists() else str(path),
                    "passed": passed,
                    "blocking": True,
                })
                if not passed:
                    errors.append({"code": name, "message": f"Required path missing: {path}"})

            project_input = self.cautomation_root() / "projects" / self.project_id() / "input"
            validation_config = self.group("validation")
            if validation_config.get("warnWhenProjectClientContractsMissing", True) is True:
                self._warn_when_no_contract_files(
                    root=project_input / "client",
                    warning_code="project_client_contracts_missing",
                    message="No project-level client contracts are present. This run is valid as a module-reference context package.",
                    warnings=warnings,
                )
            if validation_config.get("warnWhenProjectEngineeringContractsMissing", True) is True:
                self._warn_when_no_contract_files(
                    root=project_input / "engineering",
                    warning_code="project_engineering_contracts_missing",
                    message="No project-level engineering contracts are present. Module ATS is used as the implementation contract for this reference run.",
                    warnings=warnings,
                )

            status = self.status_from(warnings, errors)
            state_payload = {"status": status, "checks": checks, "warnings": warnings, "errors": errors}
            self.write_state_json("02_validate_inputs.json", state_payload)
            report = self.base_report(status, started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"validation": state_payload})
            report_path = self.write_task_report(report)
            if status == "FAILED":
                print_failed(f"02_validate_inputs FAILED; report {self.to_project_relative_path(report_path)}")
            elif status == "PASSED_WITH_WARNINGS":
                print_warning(f"02_validate_inputs PASSED_WITH_WARNINGS; report {self.to_project_relative_path(report_path)}")
            else:
                print_passed(f"02_validate_inputs PASSED; report {self.to_project_relative_path(report_path)}")
        except Exception as exc:  # noqa: BLE001
            report = self.base_report("FAILED", started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"errors": [{"code": "unexpected_error", "message": str(exc)}], "exceptionType": type(exc).__name__})
            report_path = self.write_task_report(report)
            print_failed(f"02_validate_inputs FAILED; report {self.to_project_relative_path(report_path)}")
            raise

    def _warn_when_no_contract_files(self, root: Path, warning_code: str, message: str, warnings: list[dict[str, str]]) -> None:
        files = [path for path in root.glob("*.*") if path.name != ".gitkeep"] if root.exists() else []
        if not files:
            warnings.append({"code": warning_code, "message": message})


if __name__ == "__main__":
    ValidateInputsTask().run()
