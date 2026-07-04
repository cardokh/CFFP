"""Task 05 - Validate Context Package for Pipeline 01 Context Engineering."""

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


class ValidateContextPackageTask(ContextEngineeringSupportMixin, BaseScript):
    """Validates that the generated context package contains all configured artifacts."""

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
            build_state = self.read_state_json(self.pipeline_task_state_file("build_context_package"))
            warnings.extend(build_state.get("warnings", []))
            if build_state.get("status") == "FAILED":
                errors.append({"code": "context_package_build_failed", "message": "Cannot validate context package because build task failed."})
            else:
                package_dir = self.context_package_dir()
                expected_files = list(self.group("contextFiles").values()) + list(self.group("structuredFiles").values())
                checks.append({
                    "name": "context_package_directory_exists",
                    "path": self.to_project_relative_path(package_dir) if package_dir.exists() else str(package_dir),
                    "passed": package_dir.exists(),
                    "blocking": True,
                })
                if not package_dir.exists():
                    errors.append({"code": "context_package_directory_missing", "message": f"Context package directory missing: {package_dir}"})
                for file_name in expected_files:
                    path = package_dir / file_name
                    passed = path.exists() and path.is_file() and path.stat().st_size > 0
                    checks.append({
                        "name": f"package_file_exists::{file_name}",
                        "path": self.to_project_relative_path(path) if path.exists() else str(path),
                        "passed": passed,
                        "blocking": True,
                    })
                    if not passed:
                        errors.append({"code": "package_file_missing_or_empty", "message": f"Package file missing or empty: {path}"})

            status = self.status_from(warnings, errors)
            state_payload = {"status": status, "checks": checks, "warnings": warnings, "errors": errors}
            self.write_state_json(self.pipeline_task_state_file("validate_context_package"), state_payload)
            report = self.base_report(status, started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"validation": state_payload})
            report_path = self.write_task_report(report)
            if status == "FAILED":
                print_failed(f"validate_context_package FAILED; report {self.to_project_relative_path(report_path)}")
            elif status == "PASSED_WITH_WARNINGS":
                print_warning(f"validate_context_package PASSED_WITH_WARNINGS; report {self.to_project_relative_path(report_path)}")
            else:
                print_passed(f"validate_context_package PASSED; report {self.to_project_relative_path(report_path)}")
        except Exception as exc:  # noqa: BLE001
            report = self.base_report("FAILED", started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"errors": [{"code": "unexpected_error", "message": str(exc)}], "exceptionType": type(exc).__name__})
            report_path = self.write_task_report(report)
            print_failed(f"validate_context_package FAILED; report {self.to_project_relative_path(report_path)}")
            raise


if __name__ == "__main__":
    ValidateContextPackageTask().run()
