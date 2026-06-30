"""Workflow regression suite for the DB metadata lifecycle.

The suite executes the real metadata task scripts and the DB pipeline through
subprocesses. It temporarily changes task configuration files and metadata
content, but restores the original repository state before exiting.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


def _configure_project_import_path() -> None:
    project_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "shared").is_dir()
        ),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_failed, print_passed
from scripts.shared.script_json_utils import read_json_file, write_json_file


@dataclass(frozen=True)
class CommandResult:
    name: str
    status: str
    command: list[str]
    return_code: int
    duration_seconds: float
    stdout: str
    stderr: str
    latest_report_path: str | None
    latest_report: dict[str, Any] | None


class WorkflowFailure(RuntimeError):
    """Raised when a workflow step does not match its expected result."""


class RunMetadataWorkflowsScript(BaseScript):
    """Runs deterministic metadata lifecycle workflows against real DB tasks."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.stop_on_failure = bool(self.config.get("stopOnFailure", True))
        self.target_metadata_root = self._resolve_project_path("targetMetadataRoot")
        self.target_module = self._get_required_string("targetModule")
        self.target_module_root = self.target_metadata_root / "modules" / self.target_module
        self.generated_table_names = self._get_string_list("generatedTableNames")
        self.scripts = self._get_path_map("scripts")
        self.config_paths = self._get_path_map("configs")
        self.negative_tests = self.config.get("negativeTests", {})
        self.tmp_root = self.script_directory / "tmp"
        self._metadata_snapshot = self.script_directory / "tmp_snapshot_metadata"
        self._config_snapshots: dict[Path, Any] = {}
        self.workflow_results: list[dict[str, Any]] = []

    def run(self) -> None:
        started = time.perf_counter()
        status = "PASSED"
        error_message: str | None = None

        self._capture_original_state()
        try:
            self._run_workflow("scenario_1_empty_generate_validate_pipeline", self._scenario_1)
            self._run_workflow("scenario_2_generate_remove_validate", self._scenario_2)
            self._run_workflow("scenario_3_remove_regenerate_validate_pipeline", self._scenario_3)
            self._run_workflow("scenario_4_repeated_regeneration_cycles", self._scenario_4)
            self._run_workflow("scenario_5_negative_cases", self._scenario_5)
        except Exception as error:
            status = "FAILED"
            error_message = str(error)
            if not isinstance(error, WorkflowFailure):
                raise
        finally:
            self._restore_original_state()
            report = self._build_report(status, started, error_message)
            self.write_json_report(report)

        if status == "PASSED":
            print_passed(f"run_metadata_workflows: {len(self.workflow_results)} workflow(s) passed")
            return

        print_failed(f"run_metadata_workflows: {error_message}")
        raise SystemExit(1)

    def _run_workflow(self, name: str, workflow: Callable[[], list[dict[str, Any]]]) -> None:
        print(f"\n=== {name} ===")
        started = time.perf_counter()
        self._restore_original_state()
        steps: list[dict[str, Any]] = []
        try:
            steps = workflow()
            self.workflow_results.append(
                {
                    "name": name,
                    "status": "PASSED",
                    "durationSeconds": round(time.perf_counter() - started, 4),
                    "steps": steps,
                }
            )
            print_passed(name)
        except Exception as error:
            self.workflow_results.append(
                {
                    "name": name,
                    "status": "FAILED",
                    "durationSeconds": round(time.perf_counter() - started, 4),
                    "steps": steps,
                    "error": str(error),
                }
            )
            print_failed(f"{name}: {error}")
            if self.stop_on_failure:
                raise WorkflowFailure(f"{name}: {error}") from error

    def _scenario_1(self) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        steps.append(self._remove_tables(self.generated_table_names, "prepare_empty_metadata"))
        self._assert_tables_absent(self.generated_table_names)
        steps.append(self._generate())
        self._assert_tables_present(self.generated_table_names)
        steps.append(self._validate())
        steps.append(self._db_pipeline())
        return steps

    def _scenario_2(self) -> list[dict[str, Any]]:
        selected_tables = self.generated_table_names[:2]
        remaining_tables = self.generated_table_names[2:]
        steps: list[dict[str, Any]] = []
        steps.append(self._remove_tables(self.generated_table_names, "prepare_empty_metadata"))
        steps.append(self._generate())
        steps.append(self._remove_tables(selected_tables, "remove_selected_tables"))
        self._assert_tables_absent(selected_tables)
        self._assert_tables_present(remaining_tables)
        steps.append(self._validate())
        return steps

    def _scenario_3(self) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        steps.append(self._generate_if_needed())
        steps.append(self._remove_tables(self.generated_table_names, "remove_all_generated_tables"))
        self._assert_tables_absent(self.generated_table_names)
        steps.append(self._generate())
        self._assert_tables_present(self.generated_table_names)
        steps.append(self._validate())
        steps.append(self._db_pipeline())
        return steps

    def _scenario_4(self) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        for cycle in range(1, 4):
            steps.append(self._remove_tables(self.generated_table_names, f"cycle_{cycle}_remove"))
            self._assert_tables_absent(self.generated_table_names)
            steps.append(self._generate(f"cycle_{cycle}_generate"))
            self._assert_tables_present(self.generated_table_names)
        steps.append(self._validate())
        steps.append(self._db_pipeline())
        return steps

    def _scenario_5(self) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        steps.append(self._generate_if_needed())
        before_tables = self._read_registered_tables()

        missing_table = self._get_negative_string("missingTableName")
        missing_step = self._remove_tables([missing_table], "remove_missing_table", expect_success=True)
        missing_report = missing_step.get("latestReport") or {}
        removal = missing_report.get("removal", {})
        if missing_table not in removal.get("missingTables", []):
            raise AssertionError("Missing-table removal did not report the table as missing.")
        if self._read_registered_tables() != before_tables:
            raise AssertionError("Missing-table removal changed the metadata registry.")
        steps.append(missing_step)

        steps.append(
            self._remove_tables(
                [self.generated_table_names[0], self.generated_table_names[0]],
                "duplicate_removal_table_names",
                expect_success=False,
            )
        )
        self._assert_registered_tables_equal(before_tables)

        steps.append(self._remove_tables([], "empty_removal_list", expect_success=False))
        self._assert_registered_tables_equal(before_tables)

        steps.append(self._generate_with_architecture_specifications([], "empty_specification_list", expect_success=False))
        self._assert_registered_tables_equal(before_tables)

        malformed_path = self._write_malformed_specification()
        malformed_entry = {
            "name": "malformed_specification",
            "path": self._to_generate_script_relative_path(malformed_path),
            "generatedTablesPath": "input/generated/workflows/generated_tables_malformed.json",
        }
        steps.append(
            self._generate_with_architecture_specifications(
                [malformed_entry],
                "malformed_specification_document",
                expect_success=False,
            )
        )
        self._assert_registered_tables_equal(before_tables)
        return steps

    def _generate_if_needed(self) -> dict[str, Any]:
        missing = [table for table in self.generated_table_names if table not in self._read_registered_tables()]
        if not missing:
            return {"name": "generate_if_needed", "status": "SKIPPED", "reason": "All generated tables are already present."}
        return self._generate("generate_if_needed")

    def _generate(self, step_name: str = "generate_metadata") -> dict[str, Any]:
        self._restore_config("generateTableMetadata")
        return self._run_script_step(step_name, self.scripts["generateTableMetadata"], expect_success=True)

    def _generate_with_architecture_specifications(
        self,
        architecture_specifications: list[Any],
        step_name: str,
        expect_success: bool,
    ) -> dict[str, Any]:
        config_path = self.config_paths["generateTableMetadata"]
        config = read_json_file(config_path)
        config["architectureSpecifications"] = architecture_specifications
        write_json_file(config_path, config)
        return self._run_script_step(step_name, self.scripts["generateTableMetadata"], expect_success=expect_success)

    def _remove_tables(self, tables: list[str], step_name: str, expect_success: bool = True) -> dict[str, Any]:
        config_path = self.config_paths["removeMetadataTables"]
        config = read_json_file(config_path)
        config["tables"] = tables
        write_json_file(config_path, config)
        return self._run_script_step(step_name, self.scripts["removeMetadataTables"], expect_success=expect_success)

    def _validate(self, step_name: str = "validate_metadata") -> dict[str, Any]:
        return self._run_script_step(step_name, self.scripts["validateMetadata"], expect_success=True)

    def _db_pipeline(self, step_name: str = "run_db_pipeline") -> dict[str, Any]:
        return self._run_script_step(step_name, self.scripts["dbPipeline"], expect_success=True)

    def _run_script_step(self, step_name: str, script_path: Path, expect_success: bool) -> dict[str, Any]:
        before_reports = self._collect_output_reports(script_path)
        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
        )
        command_result = CommandResult(
            name=step_name,
            status="PASSED" if completed.returncode == 0 else "FAILED",
            command=[sys.executable, self.to_project_relative_path(script_path)],
            return_code=completed.returncode,
            duration_seconds=round(time.perf_counter() - started, 4),
            stdout=completed.stdout,
            stderr=completed.stderr,
            latest_report_path=None,
            latest_report=None,
        )
        latest_report_path = self._find_newest_output_report(script_path, before_reports)
        latest_report = read_json_file(latest_report_path) if latest_report_path else None
        command_result = CommandResult(
            **{
                **command_result.__dict__,
                "latest_report_path": self.to_project_relative_path(latest_report_path) if latest_report_path else None,
                "latest_report": latest_report,
            }
        )

        if expect_success and completed.returncode != 0:
            raise AssertionError(f"Step '{step_name}' failed unexpectedly with return code {completed.returncode}.")
        if not expect_success and completed.returncode == 0:
            raise AssertionError(f"Step '{step_name}' passed unexpectedly.")

        return self._command_result_to_report(command_result, expect_success)

    def _command_result_to_report(self, result: CommandResult, expect_success: bool) -> dict[str, Any]:
        return {
            "name": result.name,
            "status": result.status,
            "expectedStatus": "PASSED" if expect_success else "FAILED",
            "returnCode": result.return_code,
            "durationSeconds": result.duration_seconds,
            "command": result.command,
            "latestReportPath": result.latest_report_path,
            "latestReport": result.latest_report,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def _capture_original_state(self) -> None:
        if self._metadata_snapshot.exists():
            shutil.rmtree(self._metadata_snapshot)
        if self.target_module_root.exists():
            shutil.copytree(self.target_module_root, self._metadata_snapshot)
        self._config_snapshots = {
            config_path: read_json_file(config_path)
            for config_path in self.config_paths.values()
        }

    def _restore_original_state(self) -> None:
        if self._metadata_snapshot.exists():
            if self.target_module_root.exists():
                shutil.rmtree(self.target_module_root)
            shutil.copytree(self._metadata_snapshot, self.target_module_root)
        for config_path, config in self._config_snapshots.items():
            write_json_file(config_path, config)
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def _restore_config(self, config_key: str) -> None:
        config_path = self.config_paths[config_key]
        write_json_file(config_path, self._config_snapshots[config_path])

    def _read_registered_tables(self) -> list[str]:
        registry_path = self.target_module_root / "tables.json"
        registry = read_json_file(registry_path)
        tables = registry.get("tables")
        if not isinstance(tables, list):
            raise AssertionError(f"Invalid metadata table registry: {registry_path}")
        return [str(table) for table in tables]

    def _assert_tables_present(self, table_names: list[str]) -> None:
        registered = set(self._read_registered_tables())
        missing = [table for table in table_names if table not in registered]
        missing_folders = [table for table in table_names if not (self.target_module_root / "tables" / table).is_dir()]
        if missing or missing_folders:
            raise AssertionError(f"Expected tables are missing. registry={missing}, folders={missing_folders}")

    def _assert_tables_absent(self, table_names: list[str]) -> None:
        registered = set(self._read_registered_tables())
        still_registered = [table for table in table_names if table in registered]
        existing_folders = [table for table in table_names if (self.target_module_root / "tables" / table).exists()]
        if still_registered or existing_folders:
            raise AssertionError(
                f"Expected tables were not removed. registry={still_registered}, folders={existing_folders}"
            )

    def _assert_registered_tables_equal(self, expected_tables: list[str]) -> None:
        actual_tables = self._read_registered_tables()
        if actual_tables != expected_tables:
            raise AssertionError(f"Metadata registry changed unexpectedly. expected={expected_tables}, actual={actual_tables}")

    def _write_malformed_specification(self) -> Path:
        malformed_path = self.project_root / self._get_negative_string("malformedSpecificationPath")
        malformed_path.parent.mkdir(parents=True, exist_ok=True)
        write_json_file(
            malformed_path,
            {
                "name": "malformed_specification",
                "version": "1.0.0",
                "targetModule": self.target_module,
                "tables": "not-a-list",
            },
        )
        return malformed_path

    def _to_generate_script_relative_path(self, path: Path) -> str:
        generate_script_directory = self.scripts["generateTableMetadata"].parent
        return path.relative_to(generate_script_directory).as_posix()

    def _collect_output_reports(self, script_path: Path) -> set[Path]:
        output_directory = script_path.parent / "output"
        if not output_directory.exists():
            return set()
        return set(output_directory.glob(f"{script_path.stem}_*.json"))

    def _find_newest_output_report(self, script_path: Path, before_reports: set[Path]) -> Path | None:
        output_directory = script_path.parent / "output"
        if not output_directory.exists():
            return None
        new_reports = [path for path in output_directory.glob(f"{script_path.stem}_*.json") if path not in before_reports]
        if not new_reports:
            return None
        return max(new_reports, key=lambda path: path.stat().st_mtime)

    def _build_report(self, status: str, started: float, error_message: str | None) -> dict[str, Any]:
        failed = [workflow for workflow in self.workflow_results if workflow["status"] == "FAILED"]
        report: dict[str, Any] = {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "metadata_lifecycle_workflows"),
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "summary": {
                "status": status,
                "workflowCount": len(self.workflow_results),
                "passedWorkflowCount": len(self.workflow_results) - len(failed),
                "failedWorkflowCount": len(failed),
                "durationSeconds": round(time.perf_counter() - started, 4),
                "details": "Workflow steps execute the real metadata task scripts and DB pipeline.",
            },
            "targetMetadataRoot": self.to_project_relative_path(self.target_metadata_root),
            "targetModule": self.target_module,
            "generatedTableNames": self.generated_table_names,
            "workflows": self.workflow_results,
        }
        if error_message:
            report["error"] = error_message
        return report

    def _resolve_project_path(self, config_key: str) -> Path:
        value = self._get_required_string(config_key)
        path = Path(value)
        return path if path.is_absolute() else self.project_root / path

    def _get_required_string(self, config_key: str) -> str:
        value = self.config.get(config_key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Config must contain non-empty '{config_key}'.")
        return value

    def _get_negative_string(self, config_key: str) -> str:
        if not isinstance(self.negative_tests, dict):
            raise ValueError("Config value 'negativeTests' must be an object.")
        value = self.negative_tests.get(config_key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"negativeTests must contain non-empty '{config_key}'.")
        return value

    def _get_string_list(self, config_key: str) -> list[str]:
        value = self.config.get(config_key)
        if not isinstance(value, list) or not value:
            raise ValueError(f"Config must contain non-empty '{config_key}' list.")
        normalized = []
        for item in value:
            if not isinstance(item, str) or not item:
                raise ValueError(f"Every '{config_key}' item must be a non-empty string.")
            normalized.append(item)
        return normalized

    def _get_path_map(self, config_key: str) -> dict[str, Path]:
        value = self.config.get(config_key)
        if not isinstance(value, dict) or not value:
            raise ValueError(f"Config must contain non-empty '{config_key}' object.")
        paths: dict[str, Path] = {}
        for key, raw_path in value.items():
            if not isinstance(raw_path, str) or not raw_path:
                raise ValueError(f"Every '{config_key}' path must be a non-empty string.")
            path = Path(raw_path)
            paths[str(key)] = path if path.is_absolute() else self.project_root / path
        return paths


if __name__ == "__main__":
    RunMetadataWorkflowsScript().run()
