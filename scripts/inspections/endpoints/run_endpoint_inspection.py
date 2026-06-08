import subprocess
import sys
from typing import Any

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_constants import (
    STATUS_ERROR,
    STATUS_FAILED,
    STATUS_PASSED,
    STATUS_SKIPPED,
)
from scripts.shared.script_json_utils import write_json_file


class EndpointInspectionRunnerScript(BaseScript):
    def __init__(self):
        super().__init__(__file__)

    def run(self) -> None:
        results = self._execute_scripts()
        summary = self._build_summary(results)

        self._write_summary(summary)
        self._print_summary(summary)

    def _execute_scripts(self) -> list[dict[str, Any]]:
        results = []
        results_by_name = {}

        for script_config in self._get_script_configs():
            result = self._execute_script_config(
                script_config=script_config,
                results_by_name=results_by_name,
            )

            results.append(result)
            results_by_name[result["name"]] = result

        return results

    def _execute_script_config(
        self,
        script_config: dict,
        results_by_name: dict,
    ) -> dict[str, Any]:
        if not script_config.get("enabled", True):
            return self._build_skipped_result(
                script_config=script_config,
                reason="Script disabled in configuration.",
            )

        if self._has_failed_dependency(
            script_config=script_config,
            results_by_name=results_by_name,
        ):
            return self._build_skipped_result(
                script_config=script_config,
                reason="One or more dependencies did not pass.",
            )

        return self._run_script(script_config)

    def _has_failed_dependency(
        self,
        script_config: dict,
        results_by_name: dict,
    ) -> bool:
        for dependency_name in script_config.get("dependsOn", []):
            dependency_result = results_by_name.get(dependency_name)

            if dependency_result is None:
                return True

            if dependency_result["status"] != STATUS_PASSED:
                return True

        return False

    def _build_skipped_result(
        self,
        script_config: dict,
        reason: str,
    ) -> dict[str, Any]:
        return {
            "name": script_config["name"],
            "module": script_config["module"],
            "status": STATUS_SKIPPED,
            "reason": reason,
            "returnCode": None,
            "stdout": "",
            "stderr": "",
        }

    def _run_script(
        self,
        script_config: dict,
    ) -> dict[str, Any]:
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                script_config["module"],
            ],
            cwd=self.project_root,
            capture_output=True,
            text=True,
        )

        normalized_stdout = self._normalize_output_text(
            process.stdout.strip(),
        )

        normalized_stderr = self._normalize_output_text(
            process.stderr.strip(),
        )

        status = self._get_script_status(
            stdout=normalized_stdout,
            return_code=process.returncode,
        )

        return {
            "name": script_config["name"],
            "module": script_config["module"],
            "status": status,
            "reason": None,
            "returnCode": process.returncode,
            "stdout": normalized_stdout,
            "stderr": normalized_stderr,
        }

    def _get_script_status(
        self,
        stdout: str,
        return_code: int,
    ) -> str:
        if return_code != 0:
            return STATUS_ERROR

        first_token = stdout.strip().split(" ", 1)[0]

        if first_token in {
            STATUS_PASSED,
            STATUS_FAILED,
            STATUS_ERROR,
            STATUS_SKIPPED,
        }:
            return first_token

        return STATUS_PASSED

    def _build_summary(
        self,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        status = STATUS_PASSED

        if any(
            result["status"]
            in {
                STATUS_FAILED,
                STATUS_ERROR,
            }
            for result in results
        ):
            status = STATUS_FAILED

        return {
            "scriptName": self.script_name,
            "mode": self.config.get(
                "mode",
                "run",
            ),
            "status": status,
            "timestamp": self.timestamp,
            "scriptCount": len(results),
            "passedCount": sum(
                1 for result in results if result["status"] == STATUS_PASSED
            ),
            "failedCount": sum(
                1 for result in results if result["status"] == STATUS_FAILED
            ),
            "errorCount": sum(
                1 for result in results if result["status"] == STATUS_ERROR
            ),
            "skippedCount": sum(
                1 for result in results if result["status"] == STATUS_SKIPPED
            ),
            "scripts": results,
        }

    def _write_summary(
        self,
        summary: dict,
    ) -> None:
        write_json_file(
            self._get_output_file_path(),
            summary,
        )

    def _print_summary(
        self,
        summary: dict,
    ) -> None:
        message = (
            "endpoint inspection runner: "
            f"passed={summary['passedCount']} "
            f"failed={summary['failedCount']} "
            f"errors={summary['errorCount']} "
            f"skipped={summary['skippedCount']} "
            f"output={self.to_project_relative_path(self._get_output_file_path())}"
        )

        if summary["status"] == STATUS_PASSED:
            print_passed(message)
            return

        print_failed(message)

    def _normalize_output_text(
        self,
        text: str,
    ) -> str:
        normalized_project_root = str(self.project_root).replace("\\", "/")
        normalized_text = text.replace("\\", "/")

        return normalized_text.replace(
            normalized_project_root,
            ".",
        )

    def _get_script_configs(self) -> list[dict]:
        scripts = self.config.get("scripts")

        if not isinstance(scripts, list):
            raise ValueError("Config must contain 'scripts' list.")

        return scripts

    def _get_output_file_path(self):
        output_file_path = self.config.get("outputFilePath")

        if isinstance(output_file_path, str) and output_file_path:
            return self.project_root / output_file_path

        output_file_name = self.config.get("outputFileName")

        if isinstance(output_file_name, str) and output_file_name:
            return self.output_directory / output_file_name

        return (
            self.output_directory / f"{self.script_name}_output_{self.timestamp}.json"
        )


def main() -> None:
    try:
        EndpointInspectionRunnerScript().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
