"""Runs the database CRUD automation pipeline by delegating to configured tasks."""

import json
import subprocess
import sys
import time
from pathlib import Path


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


class DatabaseCrudPipelineScript(BaseScript):
    """Pipeline-level entry point for database CRUD automation."""

    def __init__(self):
        super().__init__(__file__)
        self.execution = self._get_execution_config()
        self.database_engine = self._get_database_engine()
        self.components = self._get_components()
        self.component_results = []

    def run(self) -> None:
        started = time.perf_counter()
        status = "PASSED"

        try:
            self._validate_database_engine()
            self._sync_engine_execution_config()

            for component in self.components:
                if component.get("enabled") is False:
                    self.component_results.append(self._build_skipped_result(component))
                    continue

                result = self._run_component(component)
                self.component_results.append(result)

                if result["status"] != "PASSED" and self.execution.get("stopOnFailure", True) is True:
                    status = "FAILED"
                    break

            if any(result["status"] == "FAILED" for result in self.component_results):
                status = "FAILED"

            report = self._build_report(status, started)
            self.write_json_report(report)

            if status == "PASSED":
                print_passed(
                    f"db_pipeline: {report['summary']['executedComponentCount']} components executed successfully"
                )
            else:
                print_failed("db_pipeline failed. See db/output for the task report.")
                raise SystemExit(1)
        except Exception as exc:
            report = self._build_report("FAILED", started, str(exc))
            self.write_json_report(report)
            print_failed(f"db_pipeline failed: {exc}")
            raise

    def _get_execution_config(self) -> dict:
        execution = self.config.get("execution", {})
        if not isinstance(execution, dict):
            raise ValueError("db_pipeline.json execution must be an object when provided.")
        return execution

    def _get_database_engine(self) -> str:
        database_engine = self.config.get("databaseEngine")
        if not isinstance(database_engine, str) or not database_engine:
            raise ValueError("db_pipeline.json must contain non-empty 'databaseEngine'.")
        return database_engine

    def _get_components(self) -> list[dict]:
        components = self.config.get("components")
        if not isinstance(components, list) or not components:
            raise ValueError("db_pipeline.json must contain non-empty 'components'.")
        return components

    def _validate_database_engine(self) -> None:
        engine_folder = self.script_directory / self.database_engine
        if not engine_folder.is_dir():
            raise ValueError(f"Database engine folder not found: {engine_folder}")

    def _sync_engine_execution_config(self) -> None:
        create_db_schema_config_path = self.script_directory / self.database_engine / "create_db_schema" / "config" / "create_db_schema.json"
        if not create_db_schema_config_path.exists():
            return

        with open(create_db_schema_config_path, "r", encoding="utf-8") as file:
            create_db_schema_config = json.load(file)

        create_db_schema_config["execution"] = {
            "recreateDatabase": self.execution.get("recreateDatabase", False),
            "dropUnlistedTables": self.execution.get("dropUnlistedTables", False),
            "recreateExistingTables": self.execution.get("recreateExistingTables", True),
        }

        with open(create_db_schema_config_path, "w", encoding="utf-8") as file:
            json.dump(create_db_schema_config, file, indent=4)

    def _run_component(self, component: dict) -> dict:
        name = self._get_required_string(component, "name")
        script_path = self.project_root / self._get_required_string(component, "scriptPath")

        if not script_path.exists():
            return {
                "name": name,
                "status": "FAILED",
                "scriptPath": self.to_project_relative_path(script_path),
                "durationSeconds": 0,
                "returnCode": None,
                "stdout": "",
                "stderr": f"Script not found: {script_path}",
            }

        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
        )

        return {
            "name": name,
            "status": "PASSED" if completed.returncode == 0 else "FAILED",
            "scriptPath": self.to_project_relative_path(script_path),
            "durationSeconds": round(time.perf_counter() - started, 4),
            "returnCode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _build_skipped_result(self, component: dict) -> dict:
        return {
            "name": self._get_required_string(component, "name"),
            "status": "SKIPPED",
            "scriptPath": component.get("scriptPath", ""),
            "durationSeconds": 0,
            "returnCode": None,
            "stdout": "",
            "stderr": "",
        }

    def _build_report(self, status: str, started: float, error: str | None = None) -> dict:
        executed = [result for result in self.component_results if result["status"] != "SKIPPED"]
        skipped = [result for result in self.component_results if result["status"] == "SKIPPED"]
        failed = [result for result in self.component_results if result["status"] == "FAILED"]

        report = {
            "scriptName": self.script_name,
            "mode": self.config.get("mode", "database_crud_pipeline"),
            "databaseEngine": self.database_engine,
            "summary": {
                "status": status,
                "executedComponentCount": len(executed),
                "skippedComponentCount": len(skipped),
                "failedComponentCount": len(failed),
                "durationSeconds": round(time.perf_counter() - started, 4),
                "details": "See each component output folder for detailed reports.",
            },
            "execution": self.execution,
            "components": self.component_results,
        }

        if error:
            report["error"] = error

        return report

    def _get_required_string(self, source: dict, key: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Component must contain non-empty '{key}'.")
        return value


if __name__ == "__main__":
    DatabaseCrudPipelineScript().run()
