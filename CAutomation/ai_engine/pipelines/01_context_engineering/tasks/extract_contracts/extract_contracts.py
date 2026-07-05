"""Task 03 - Extract Contracts for Pipeline 01 Context Engineering."""

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
    source_record,
    utc_now_iso,
)

configure_project_import_path(__file__)

from scripts.shared.base_script import BaseScript  # noqa: E402
from scripts.shared.script_console_utils import print_failed, print_passed  # noqa: E402
from scripts.shared.script_json_utils import read_json_file  # noqa: E402


class ExtractContractsTask(ContextEngineeringSupportMixin, BaseScript):
    """Copies normalized input contracts into deterministic extraction state files."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.pipeline_config: dict[str, Any] = self.load_pipeline_config()

    def run(self) -> None:
        started = time.perf_counter()
        started_at_utc = utc_now_iso()
        warnings: list[dict[str, str]] = []
        errors: list[dict[str, str]] = []
        generated_files: list[str] = []
        try:
            normalization_state = self.read_state_json(self.pipeline_task_state_file("normalize_input_documents"))
            if normalization_state.get("status") == "FAILED":
                errors.append({"code": "input_normalization_failed", "message": "Cannot extract contracts because input normalization failed."})
            else:
                normalized_documents = normalization_state.get("documents", {})
                srs_markdown_path = self._required_normalized_path(normalized_documents, "srs")
                ats_markdown_path = self._required_normalized_path(normalized_documents, "ats")
                extracted_dir = self.ensure_state_root() / "extracted_contracts"
                extracted_dir.mkdir(parents=True, exist_ok=True)
                srs_markdown = srs_markdown_path.read_text(encoding="utf-8")
                ats_markdown = ats_markdown_path.read_text(encoding="utf-8")
                srs_output = extracted_dir / "module_srs.md"
                ats_output = extracted_dir / "module_ats.md"
                srs_output.write_text(srs_markdown, encoding="utf-8", newline="\n")
                ats_output.write_text(ats_markdown, encoding="utf-8", newline="\n")
                generated_files.extend([self.to_project_relative_path(srs_output), self.to_project_relative_path(ats_output)])
                project = read_json_file(self.project_config_path())
                source_files = []
                manifest_path_value = normalization_state.get("normalizationManifestPath")
                if isinstance(manifest_path_value, str) and manifest_path_value:
                    source_files.append(source_record(self, self.CAutomation_root().parent / manifest_path_value, "normalized_input_manifest", "json"))
                source_files.extend([
                    source_record(self, srs_markdown_path, "module_srs", "markdown"),
                    source_record(self, ats_markdown_path, "module_ats", "markdown"),
                    source_record(self, self.project_config_path(), "project_config", "json"),
                ])
                self.write_state_json(
                    self.pipeline_task_state_file("extract_contracts"),
                    {
                        "status": "PASSED",
                        "project": project,
                        "srsMarkdownPath": self.to_project_relative_path(srs_output),
                        "atsMarkdownPath": self.to_project_relative_path(ats_output),
                        "normalizedInputRoot": normalization_state.get("normalizedInputRoot"),
                        "sourceFiles": source_files,
                        "generatedFiles": generated_files,
                    },
                )

            status = self.status_from(warnings, errors)
            if errors:
                self.write_state_json(self.pipeline_task_state_file("extract_contracts"), {"status": status, "warnings": warnings, "errors": errors})
            report = self.base_report(status, started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"summary": {"generatedFiles": generated_files}, "warnings": warnings, "errors": errors})
            report_path = self.write_task_report(report)
            if status == "FAILED":
                print_failed(f"extract_contracts FAILED; report {self.to_project_relative_path(report_path)}")
            else:
                print_passed(f"extract_contracts PASSED; report {self.to_project_relative_path(report_path)}")
        except Exception as exc:  # noqa: BLE001
            report = self.base_report("FAILED", started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"errors": [{"code": "unexpected_error", "message": str(exc)}], "exceptionType": type(exc).__name__})
            report_path = self.write_task_report(report)
            print_failed(f"extract_contracts FAILED; report {self.to_project_relative_path(report_path)}")
            raise

    def _required_normalized_path(self, documents: Any, document_id: str) -> Path:
        if not isinstance(documents, dict):
            raise RuntimeError("Normalization state does not contain documents object.")
        document = documents.get(document_id)
        if not isinstance(document, dict):
            raise RuntimeError(f"Normalization state is missing document: {document_id}")
        value = document.get("normalizedPath")
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"Normalization state is missing normalizedPath for document: {document_id}")
        path = self.CAutomation_root().parent / value
        if not path.exists():
            raise RuntimeError(f"Normalized document does not exist: {path}")
        return path


if __name__ == "__main__":
    ExtractContractsTask().run()
