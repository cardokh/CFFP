"""
Automation task validation.

Responsibilities:
- Validate registered automation tasks before execution exists.
- Verify script and configuration paths safely inside the project root.
- Reuse the existing script governance inspector for script compliance checks.
- Return UI-friendly validation reports without executing the target automation task.
"""

import contextlib
import io
import json
import sys
from pathlib import Path


VALIDATION_STATUS_PASSED = "PASSED"
VALIDATION_STATUS_FAILED = "FAILED"

CHECK_TASK_REGISTERED = "task-registered"
CHECK_SCRIPT_PATH = "script-path"
CHECK_CONFIGURATION_PATH = "configuration-path"
CHECK_CONFIGURATION_JSON = "configuration-json"
CHECK_SCRIPT_GOVERNANCE = "script-governance"


class AutomationTaskValidationService:
    def __init__(
        self,
        project_root,
    ):
        self.project_root = Path(project_root).resolve()

    def validate_task(self, automation_task) -> dict:
        checks = [
            self._build_passed_check(
                CHECK_TASK_REGISTERED,
                "Task is registered",
                "The task was found in the automation task registry.",
            ),
        ]

        script_path_result = self._validate_project_relative_file_path(
            check_id=CHECK_SCRIPT_PATH,
            label="Script path",
            relative_path=automation_task.script_path,
            missing_message="The registered script file does not exist.",
        )
        checks.append(script_path_result["check"])

        config_path_result = self._validate_project_relative_file_path(
            check_id=CHECK_CONFIGURATION_PATH,
            label="Configuration path",
            relative_path=automation_task.config_path,
            missing_message="The registered configuration file does not exist.",
        )
        checks.append(config_path_result["check"])

        checks.append(
            self._validate_configuration_json(
                config_path_result["path"],
            )
        )

        governance_report = self._validate_script_governance(
            script_path_result["path"],
        )
        checks.append(governance_report["check"])

        return self._build_validation_report(
            automation_task=automation_task,
            checks=checks,
            governance_report=governance_report,
        )

    def _validate_project_relative_file_path(
        self,
        check_id: str,
        label: str,
        relative_path: str,
        missing_message: str,
    ) -> dict:
        normalized_relative_path = str(relative_path or "").strip()

        if not normalized_relative_path:
            return {
                "path": None,
                "check": self._build_failed_check(
                    check_id,
                    label,
                    "The path is empty.",
                ),
            }

        candidate_path = (self.project_root / normalized_relative_path).resolve()

        if not self._is_within_project_root(candidate_path):
            return {
                "path": candidate_path,
                "check": self._build_failed_check(
                    check_id,
                    label,
                    "The path escapes the project root.",
                    {
                        "path": normalized_relative_path,
                    },
                ),
            }

        if not candidate_path.is_file():
            return {
                "path": candidate_path,
                "check": self._build_failed_check(
                    check_id,
                    label,
                    missing_message,
                    {
                        "path": normalized_relative_path,
                    },
                ),
            }

        return {
            "path": candidate_path,
            "check": self._build_passed_check(
                check_id,
                label,
                "The file exists and stays inside the project root.",
                {
                    "path": normalized_relative_path,
                },
            ),
        }

    def _validate_configuration_json(self, config_path: Path | None) -> dict:
        if config_path is None or not config_path.is_file():
            return self._build_failed_check(
                CHECK_CONFIGURATION_JSON,
                "Configuration JSON",
                "The configuration file could not be loaded because the path is invalid.",
            )

        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                json.load(config_file)
        except json.JSONDecodeError as error:
            return self._build_failed_check(
                CHECK_CONFIGURATION_JSON,
                "Configuration JSON",
                "The configuration file is not valid JSON.",
                {
                    "line": error.lineno,
                    "column": error.colno,
                    "message": error.msg,
                },
            )

        return self._build_passed_check(
            CHECK_CONFIGURATION_JSON,
            "Configuration JSON",
            "The configuration file is valid JSON.",
        )

    def _validate_script_governance(self, script_path: Path | None) -> dict:
        if script_path is None or not script_path.is_file():
            return {
                "check": self._build_failed_check(
                    CHECK_SCRIPT_GOVERNANCE,
                    "Script governance",
                    "Script governance inspection could not run because the script path is invalid.",
                ),
                "output": "",
                "script_report": None,
            }

        try:
            ScriptGovernanceInspector = self._load_script_governance_inspector()
            inspector = ScriptGovernanceInspector()
            inspector.config["targetScripts"] = [
                self._to_project_relative_path(script_path),
            ]

            captured_output = io.StringIO()

            with contextlib.redirect_stdout(captured_output):
                inspector.run()

            script_report = inspector.script_reports[0] if inspector.script_reports else None

            status = (
                script_report.get("summary", {}).get("status", VALIDATION_STATUS_FAILED)
                if script_report
                else VALIDATION_STATUS_FAILED
            )

            if status == VALIDATION_STATUS_PASSED:
                check = self._build_passed_check(
                    CHECK_SCRIPT_GOVERNANCE,
                    "Script governance",
                    "The script passed the existing script governance inspector.",
                )
            else:
                check = self._build_failed_check(
                    CHECK_SCRIPT_GOVERNANCE,
                    "Script governance",
                    "The script failed the existing script governance inspector.",
                )

            return {
                "check": check,
                "output": captured_output.getvalue().strip(),
                "script_report": script_report,
            }

        except Exception as error:
            return {
                "check": self._build_failed_check(
                    CHECK_SCRIPT_GOVERNANCE,
                    "Script governance",
                    "Script governance inspection failed to complete.",
                    {
                        "error": str(error),
                    },
                ),
                "output": "",
                "script_report": None,
            }

    def _load_script_governance_inspector(self):
        project_root_text = str(self.project_root)

        if project_root_text not in sys.path:
            sys.path.insert(0, project_root_text)

        from scripts.inspections.governed.inspect_script_governance import (
            ScriptGovernanceInspector,
        )

        return ScriptGovernanceInspector


    def _build_validation_report(
        self,
        automation_task,
        checks: list[dict],
        governance_report: dict,
    ) -> dict:
        failed_checks = [check for check in checks if check["status"] == VALIDATION_STATUS_FAILED]

        return {
            "task_id": automation_task.task_id,
            "status": VALIDATION_STATUS_FAILED if failed_checks else VALIDATION_STATUS_PASSED,
            "summary": {
                "check_count": len(checks),
                "passed_check_count": len(checks) - len(failed_checks),
                "failed_check_count": len(failed_checks),
            },
            "checks": checks,
            "governance": {
                "terminal_output": governance_report.get("output", ""),
                "script_report": governance_report.get("script_report"),
            },
        }

    def _build_passed_check(
        self,
        check_id: str,
        label: str,
        message: str,
        details: dict | None = None,
    ) -> dict:
        return self._build_check(
            check_id=check_id,
            label=label,
            status=VALIDATION_STATUS_PASSED,
            message=message,
            details=details,
        )

    def _build_failed_check(
        self,
        check_id: str,
        label: str,
        message: str,
        details: dict | None = None,
    ) -> dict:
        return self._build_check(
            check_id=check_id,
            label=label,
            status=VALIDATION_STATUS_FAILED,
            message=message,
            details=details,
        )

    def _build_check(
        self,
        check_id: str,
        label: str,
        status: str,
        message: str,
        details: dict | None = None,
    ) -> dict:
        check = {
            "id": check_id,
            "label": label,
            "status": status,
            "message": message,
        }

        if details is not None:
            check["details"] = details

        return check

    def _is_within_project_root(self, candidate_path: Path) -> bool:
        try:
            candidate_path.relative_to(self.project_root)
            return True
        except ValueError:
            return False

    def _to_project_relative_path(self, file_path: Path) -> str:
        return str(file_path.relative_to(self.project_root)).replace(
            "\\",
            "/",
        )
