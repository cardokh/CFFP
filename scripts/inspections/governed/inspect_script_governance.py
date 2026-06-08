from pathlib import Path

from scripts.shared.base_script import BaseScript
from scripts.shared.script_json_utils import read_json_file
from scripts.shared.script_json_utils import write_json_file


class ScriptGovernanceInspector(BaseScript):
    """
    Inspects project scripts against scripting blueprint governance expectations.
    """

    def __init__(self):
        super().__init__(__file__)
        self.findings = []
        self.script_reports = []
        self.rules_by_id = {}

    def run(self) -> None:
        blueprint_rules = self._load_blueprint_rules()

        self.rules_by_id = self._build_rules_by_id(
            blueprint_rules,
        )

        target_scripts = self._resolve_target_scripts()

        for target_script in target_scripts:
            script_report = self._inspect_target_script(
                target_script,
                blueprint_rules,
            )

            self.script_reports.append(script_report)
            self._write_script_report(script_report)

        summary_report = self._build_summary_report(target_scripts)
        self._write_summary_report(summary_report)

        self._print_summary(summary_report)

    def _print_summary(
        self,
        summary_report: dict,
    ) -> None:
        status = summary_report["summary"]["status"]
        inspected_count = summary_report["summary"]["inspectedScriptCount"]
        failed_count = summary_report["summary"]["failedScriptCount"]

        prefix = "FAIL" if status == "FAILED" else "PASS"

        message = (
            f"{failed_count} failed script(s)"
            if status == "FAILED"
            else f"{inspected_count} script(s) inspected"
        )

        print(f"{prefix} {self.script_name}: {message}")

    def _load_blueprint_rules(self) -> list[dict]:
        rule_file_paths = self.config.get("blueprintRuleFiles", [])
        rules = []

        for rule_file_path in rule_file_paths:
            absolute_rule_file_path = self.project_root / rule_file_path

            if not absolute_rule_file_path.exists():
                self._add_system_finding(
                    rule_id="SCRIPT-GOVERNANCE-RULE-FILE-MISSING",
                    severity="ERROR",
                    status="FAILED",
                    message="Blueprint rule file does not exist.",
                    file_path=absolute_rule_file_path,
                )
                continue

            rule_data = read_json_file(absolute_rule_file_path)

            rules.append(
                {
                    "path": self.to_project_relative_path(
                        absolute_rule_file_path,
                    ),
                    "rules": rule_data,
                }
            )

        return rules

    def _build_rules_by_id(
        self,
        blueprint_rules: list[dict],
    ) -> dict:
        rules_by_id = {}

        for rule_file in blueprint_rules:
            rule_set = rule_file.get(
                "rules",
                {},
            )

            rules = rule_set.get(
                "rules",
                [],
            )

            for rule in rules:
                rule_id = rule.get("ruleId")

                if not rule_id:
                    continue

                rules_by_id[rule_id] = rule

        return rules_by_id

    def _resolve_target_scripts(self) -> list[Path]:
        target_script_paths = self.config.get("targetScripts", [])

        return [
            self.project_root / target_script_path
            for target_script_path in target_script_paths
        ]

    def _inspect_target_script(
        self,
        target_script_path: Path,
        blueprint_rules: list[dict],
    ) -> dict:
        start_index = len(self.findings)

        if not target_script_path.exists():
            self._add_system_finding(
                rule_id="SCRIPT-GOVERNANCE-TARGET-MISSING",
                severity="ERROR",
                status="FAILED",
                message="Target script does not exist.",
                file_path=target_script_path,
            )
        else:
            script_content = target_script_path.read_text(
                encoding="utf-8",
            )

            self._validate_base_script_usage(
                target_script_path,
                script_content,
            )

            self._validate_config_driven_execution(
                target_script_path,
                script_content,
            )

            self._validate_output_architecture(
                target_script_path,
                script_content,
            )

            self._validate_concise_terminal_output(
                target_script_path,
                script_content,
            )

            self._validate_shared_utility_usage(
                target_script_path,
                script_content,
            )

            self._validate_separated_script_responsibilities(
                target_script_path,
                script_content,
            )

            self._validate_hardcoded_paths(
                target_script_path,
                script_content,
                blueprint_rules,
            )

        script_findings = self.findings[start_index:]

        return self._build_script_report(
            target_script_path,
            script_findings,
        )

    def _validate_base_script_usage(
        self,
        target_script_path: Path,
        script_content: str,
    ) -> None:
        rule_id = "SCRIPT-001"

        if not self.config.get(
            "failOnMissingBaseScript",
            True,
        ):
            return

        has_base_script_import = (
            "from scripts.shared.base_script import BaseScript" in script_content
        )

        extends_base_script = "(BaseScript)" in script_content

        calls_base_script_init = "super().__init__(__file__)" in script_content

        if has_base_script_import and extends_base_script and calls_base_script_init:
            self._add_rule_finding(
                rule_id=rule_id,
                status="PASSED",
                message="Script uses BaseScript infrastructure.",
                file_path=target_script_path,
                passed_severity="INFO",
            )
            return

        self._add_rule_finding(
            rule_id=rule_id,
            status="FAILED",
            message="Script must import, extend, and initialize BaseScript.",
            file_path=target_script_path,
        )

    def _validate_config_driven_execution(
        self,
        target_script_path: Path,
        script_content: str,
    ) -> None:
        rule_id = "SCRIPT-002"

        if not self.config.get(
            "failOnMissingConfigDrivenExecution",
            True,
        ):
            return

        if "self.config" in script_content:
            self._add_rule_finding(
                rule_id=rule_id,
                status="PASSED",
                message="Script uses config-driven execution.",
                file_path=target_script_path,
                passed_severity="INFO",
            )
            return

        self._add_rule_finding(
            rule_id=rule_id,
            status="FAILED",
            message="Script must use config-driven execution.",
            file_path=target_script_path,
        )

    def _validate_output_architecture(
        self,
        target_script_path: Path,
        script_content: str,
    ) -> None:
        rule_id = "SCRIPT-003"

        if not self.config.get(
            "failOnMissingOutputArchitecture",
            True,
        ):
            return

        uses_base_report_writer = "write_json_report" in script_content

        uses_output_directory_with_json_writer = (
            "self.output_directory" in script_content
            and "write_json_file" in script_content
        )

        if uses_base_report_writer or uses_output_directory_with_json_writer:
            self._add_rule_finding(
                rule_id=rule_id,
                status="PASSED",
                message=(
                    "Script writes detailed reports through the configured "
                    "output architecture."
                ),
                file_path=target_script_path,
                passed_severity="INFO",
            )
            return

        self._add_rule_finding(
            rule_id=rule_id,
            status="FAILED",
            message=(
                "Script must write detailed reports through its output " "architecture."
            ),
            file_path=target_script_path,
        )

    def _validate_concise_terminal_output(
        self,
        target_script_path: Path,
        script_content: str,
    ) -> None:
        rule_id = "SCRIPT-004"

        if not self.config.get(
            "failOnNonConciseTerminalOutput",
            True,
        ):
            return

        print_count = script_content.count("print(")

        if print_count <= 2:
            self._add_rule_finding(
                rule_id=rule_id,
                status="PASSED",
                message="Script terminal output appears concise.",
                file_path=target_script_path,
                passed_severity="INFO",
                details={
                    "printCount": print_count,
                },
            )
            return

        self._add_rule_finding(
            rule_id=rule_id,
            status="FAILED",
            message=(
                "Script appears to use too many direct terminal print " "statements."
            ),
            file_path=target_script_path,
            details={
                "printCount": print_count,
            },
        )

    def _validate_shared_utility_usage(
        self,
        target_script_path: Path,
        script_content: str,
    ) -> None:
        rule_id = "SCRIPT-005"

        if not self.config.get(
            "failOnMissingSharedUtilities",
            True,
        ):
            return

        if "from scripts.shared." in script_content:
            self._add_rule_finding(
                rule_id=rule_id,
                status="PASSED",
                message="Script uses shared scripting utilities.",
                file_path=target_script_path,
                passed_severity="INFO",
            )
            return

        self._add_rule_finding(
            rule_id=rule_id,
            status="FAILED",
            message="Script must use shared scripting utilities.",
            file_path=target_script_path,
        )

    def _validate_separated_script_responsibilities(
        self,
        target_script_path: Path,
        script_content: str,
    ) -> None:
        rule_id = "SCRIPT-006"

        has_run_method = "def run(" in script_content

        has_report_builder = (
            "def _build_" in script_content or "build_" in script_content
        )

        has_report_writer = (
            "def _write_" in script_content
            or "write_json_file" in script_content
            or "write_json_report" in script_content
        )

        if has_run_method and has_report_builder and has_report_writer:
            self._add_rule_finding(
                rule_id=rule_id,
                status="PASSED",
                message=(
                    "Script separates execution and reporting " "responsibilities."
                ),
                file_path=target_script_path,
                passed_severity="INFO",
            )
            return

        self._add_rule_finding(
            rule_id=rule_id,
            status="FAILED",
            message=(
                "Script should separate execution, result building, and "
                "report writing responsibilities."
            ),
            file_path=target_script_path,
        )

    def _validate_hardcoded_paths(
        self,
        target_script_path: Path,
        script_content: str,
        blueprint_rules: list[dict],
    ) -> None:
        rule_id = "SCRIPT-007"

        if not self.config.get(
            "failOnHardcodedPaths",
            True,
        ):
            return

        rule_config = self._find_rule_config(
            blueprint_rules,
            rule_id,
        )

        disallowed_fragments = rule_config.get(
            "disallowedPathFragments",
            [],
        )

        violations = [
            fragment for fragment in disallowed_fragments if fragment in script_content
        ]

        if not violations:
            self._add_rule_finding(
                rule_id=rule_id,
                status="PASSED",
                message=(
                    "Script does not contain disallowed hardcoded output "
                    "path fragments."
                ),
                file_path=target_script_path,
                passed_severity="INFO",
            )
            return

        self._add_rule_finding(
            rule_id=rule_id,
            status="FAILED",
            message="Script contains disallowed hardcoded output path fragments.",
            file_path=target_script_path,
            details={
                "violations": violations,
            },
        )

    def _find_rule_config(
        self,
        blueprint_rules: list[dict],
        rule_id: str,
    ) -> dict:
        for rule_file in blueprint_rules:
            rule_set = rule_file.get(
                "rules",
                {},
            )

            rules = rule_set.get(
                "rules",
                [],
            )

            for rule in rules:
                if rule.get("ruleId") == rule_id:
                    config = rule.get(
                        "config",
                        {},
                    )

                    if isinstance(config, dict):
                        return config

                    return {}

        return {}

    def _get_rule(
        self,
        rule_id: str,
    ) -> dict:
        return self.rules_by_id.get(
            rule_id,
            {
                "ruleId": rule_id,
                "name": "Unknown rule",
                "description": (
                    "Rule metadata was not found in the loaded blueprint "
                    "rule catalog."
                ),
                "severity": "ERROR",
            },
        )

    def _add_rule_finding(
        self,
        rule_id: str,
        status: str,
        message: str,
        file_path: Path,
        passed_severity: str = "INFO",
        details: dict | None = None,
    ) -> None:
        rule = self._get_rule(rule_id)

        severity = rule.get(
            "severity",
            "ERROR",
        )

        if status == "PASSED":
            severity = passed_severity

        finding = {
            "ruleId": rule.get(
                "ruleId",
                rule_id,
            ),
            "ruleName": rule.get(
                "name",
                "",
            ),
            "severity": severity,
            "status": status,
            "message": message,
            "ruleDescription": rule.get(
                "description",
                "",
            ),
            "filePath": self.to_project_relative_path(
                file_path,
            ),
        }

        if details is not None:
            finding["details"] = details

        self.findings.append(
            finding,
        )

    def _add_system_finding(
        self,
        rule_id: str,
        severity: str,
        status: str,
        message: str,
        file_path: Path,
        details: dict | None = None,
    ) -> None:
        finding = {
            "ruleId": rule_id,
            "ruleName": "Script governance system finding",
            "severity": severity,
            "status": status,
            "message": message,
            "ruleDescription": (
                "This finding is produced by the governance inspector runtime, "
                "not by the blueprint scripting rule catalog."
            ),
            "filePath": self.to_project_relative_path(
                file_path,
            ),
        }

        if details is not None:
            finding["details"] = details

        self.findings.append(
            finding,
        )

    def _build_script_report(
        self,
        target_script_path: Path,
        script_findings: list[dict],
    ) -> dict:
        failed_findings = [
            finding for finding in script_findings if finding["status"] == "FAILED"
        ]

        passed_findings = [
            finding for finding in script_findings if finding["status"] == "PASSED"
        ]

        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "inspect",
            ),
            "inspectedFile": self.to_project_relative_path(
                target_script_path,
            ),
            "summary": {
                "findingCount": len(script_findings),
                "passedFindingCount": len(passed_findings),
                "failedFindingCount": len(failed_findings),
                "status": ("FAILED" if failed_findings else "PASSED"),
            },
            "findings": script_findings,
        }

    def _build_summary_report(
        self,
        target_scripts: list[Path],
    ) -> dict:
        failed_scripts = [
            script_report
            for script_report in self.script_reports
            if script_report["summary"]["status"] == "FAILED"
        ]

        passed_scripts = [
            script_report
            for script_report in self.script_reports
            if script_report["summary"]["status"] == "PASSED"
        ]

        inspected_files = [
            {
                "filePath": script_report["inspectedFile"],
                "status": script_report["summary"]["status"],
                "findingCount": script_report["summary"]["findingCount"],
                "failedFindingCount": script_report["summary"]["failedFindingCount"],
            }
            for script_report in self.script_reports
        ]

        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "inspect",
            ),
            "summary": {
                "inspectedScriptCount": len(target_scripts),
                "passedScriptCount": len(passed_scripts),
                "failedScriptCount": len(failed_scripts),
                "findingCount": len(self.findings),
                "status": ("FAILED" if failed_scripts else "PASSED"),
            },
            "inspectedFiles": inspected_files,
        }

    def _write_summary_report(
        self,
        summary_report: dict,
    ) -> None:
        summary_report_path = (
            self.output_directory / f"{self.script_name}_summary_{self.timestamp}.json"
        )

        write_json_file(
            summary_report_path,
            summary_report,
        )

    def _write_script_report(
        self,
        script_report: dict,
    ) -> None:
        inspected_file_name = Path(
            script_report["inspectedFile"],
        ).stem

        report_file_path = (
            self.output_directory
            / f"{self.script_name}_{inspected_file_name}_{self.timestamp}.json"
        )

        write_json_file(
            report_file_path,
            script_report,
        )


if __name__ == "__main__":
    ScriptGovernanceInspector().run()
