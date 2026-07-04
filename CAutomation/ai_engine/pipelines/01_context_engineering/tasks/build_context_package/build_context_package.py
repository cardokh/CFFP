"""Task 04 - Build Context Package for Pipeline 01 Context Engineering."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

_TASKS_ROOT = Path(__file__).resolve().parents[1]
if str(_TASKS_ROOT) not in sys.path:
    sys.path.insert(0, str(_TASKS_ROOT))

from _shared.context_engineering_common import ContextEngineeringSupportMixin, clean_directory, configure_project_import_path, utc_now_iso  # noqa: E402

configure_project_import_path(__file__)

from scripts.shared.base_script import BaseScript  # noqa: E402
from scripts.shared.script_console_utils import print_failed, print_passed, print_warning  # noqa: E402
from scripts.shared.script_json_utils import write_json_file  # noqa: E402


class BuildContextPackageTask(ContextEngineeringSupportMixin, BaseScript):
    """Builds the deterministic context package from extracted contract state."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.pipeline_config: dict[str, Any] = self.load_pipeline_config()
        self.generated_files: list[str] = []

    def run(self) -> None:
        started = time.perf_counter()
        started_at_utc = utc_now_iso()
        warnings: list[dict[str, str]] = []
        errors: list[dict[str, str]] = []
        try:
            validation_state = self.read_state_json(self.pipeline_task_state_file("validate_inputs"))
            extraction_state = self.read_state_json(self.pipeline_task_state_file("extract_contracts"))
            warnings.extend(validation_state.get("warnings", []))
            if validation_state.get("status") == "FAILED" or extraction_state.get("status") == "FAILED":
                errors.append({"code": "previous_task_failed", "message": "Cannot build context package because a previous task failed."})
            else:
                package_dir = self.context_package_dir()
                if self.group("output").get("cleanPackageBeforeWrite", True) is True:
                    clean_directory(package_dir)
                else:
                    package_dir.mkdir(parents=True, exist_ok=True)

                srs_markdown = (self.project_root / extraction_state["srsMarkdownPath"]).read_text(encoding="utf-8")
                ats_markdown = (self.project_root / extraction_state["atsMarkdownPath"]).read_text(encoding="utf-8")
                project = extraction_state.get("project", {})
                context_outputs = self._build_context_outputs(project, srs_markdown, ats_markdown, warnings)
                for filename, content in context_outputs.items():
                    self._write_text_file(package_dir / filename, content)

                validation_status = self.status_from(warnings, errors)
                manifest = self._build_manifest(project, validation_status, sorted(context_outputs.keys()))
                provenance = self._build_provenance(extraction_state.get("sourceFiles", []))
                validation_report = {
                    "status": validation_status,
                    "checks": validation_state.get("checks", []),
                    "warnings": warnings,
                    "errors": errors,
                }
                structured_files = self.group("structuredFiles")
                self._write_json_package_file(package_dir, structured_files["manifest"], manifest)
                self._write_json_package_file(package_dir, structured_files["provenance"], provenance)
                self._write_json_package_file(package_dir, structured_files["validationReport"], validation_report)
                self.write_state_json(
                    self.pipeline_task_state_file("build_context_package"),
                    {
                        "status": validation_status,
                        "contextPackageDirectory": self.to_project_relative_path(package_dir),
                        "generatedFiles": self.generated_files,
                        "manifest": manifest,
                        "warnings": warnings,
                        "errors": errors,
                    },
                )

            status = self.status_from(warnings, errors)
            if errors:
                self.write_state_json(self.pipeline_task_state_file("build_context_package"), {"status": status, "warnings": warnings, "errors": errors})
            report = self.base_report(status, started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"summary": {"generatedFileCount": len(self.generated_files)}, "generatedFiles": self.generated_files, "warnings": warnings, "errors": errors})
            report_path = self.write_task_report(report)
            if status == "FAILED":
                print_failed(f"build_context_package FAILED; report {self.to_project_relative_path(report_path)}")
            elif status == "PASSED_WITH_WARNINGS":
                print_warning(f"build_context_package PASSED_WITH_WARNINGS; report {self.to_project_relative_path(report_path)}")
            else:
                print_passed(f"build_context_package PASSED; report {self.to_project_relative_path(report_path)}")
        except Exception as exc:  # noqa: BLE001
            report = self.base_report("FAILED", started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"errors": [{"code": "unexpected_error", "message": str(exc)}], "exceptionType": type(exc).__name__})
            report_path = self.write_task_report(report)
            print_failed(f"build_context_package FAILED; report {self.to_project_relative_path(report_path)}")
            raise

    def _build_context_outputs(self, project: dict[str, Any], srs_markdown: str, ats_markdown: str, warnings: list[dict[str, str]]) -> dict[str, str]:
        files = self.group("contextFiles")
        project_name = str(project.get("name", self.project_id()))
        return {
            files["globalContext"]: self._global_context(),
            files["projectContext"]: self._project_context(project_name),
            files["moduleContext"]: self._module_context(srs_markdown),
            files["architectureContext"]: self._architecture_context(ats_markdown),
            files["constraintsContext"]: self._constraints_context(),
            files["generationContext"]: self._generation_context(warnings),
            files["sourceIndex"]: self._source_index_context(),
            files["openQuestions"]: self._open_questions_context(warnings),
        }

    def _global_context(self) -> str:
        return f"""# Global Context

## CAutomation Principles

CAutomation is a deterministic AI-assisted software development automation package. Human-authored contracts are converted into validated, traceable context packages. Downstream planning and generation consume those packages instead of relying on conversation history or arbitrary repository inspection.

## Lifecycle

1. Context Engineering
2. Planning
3. Generation
4. Validation
5. Apply
6. Verification

## First Deliverable

{self.pipeline_config.get("firstDeliverable", "The executable CAutomation package is the first deliverable.")}
"""

    def _project_context(self, project_name: str) -> str:
        return f"""# Project Context

## Project Identity

- Project ID: `{self.project_id()}`
- Project Name: `{project_name}`
- Reference Module: `{self.module_id()}`

## Current Delivery Focus

The current automation-package reference project is the Pipeline Management module. The Context Engineering pipeline must prepare deterministic context from the approved module SRS and ATS without expanding scope to unrelated modules or project-level design work.

## Project-Level Input Status

Project-level client and engineering documents are intentionally deferred in this iteration. Their absence is recorded as a warning, not as a blocker, because this run is scoped to the approved Pipeline Management module contracts.
"""

    def _module_context(self, srs_markdown: str) -> str:
        input_config = self.group("input")
        return f"""# Module Context

## Scope

- Project: `{self.project_id()}`
- Module: `{self.module_id()}`
- Source of functional truth: `{input_config["srsFileName"]}`
- Source of technical truth: `{input_config["atsFileName"]}`

## Software Requirements Specification Extract

{srs_markdown}
"""

    def _architecture_context(self, ats_markdown: str) -> str:
        return f"""# Architecture Context

## Source Rule

The ATS implements the approved SRS. The ATS must not introduce unrelated business requirements.

## Architecture and Technical Specification Extract

{ats_markdown}
"""

    def _constraints_context(self) -> str:
        return f"""# Constraints Context

## Deterministic Generation Constraints

- Do not invent requirements that are not present in the approved SRS.
- Do not invent implementation decisions that are not present in the approved ATS.
- Do not read arbitrary repository files during downstream generation.
- Preserve the Project → Product → Module → Pipeline context model.
- Preserve the reusable Task catalog and PipelineTask association model.
- Generated artifacts are untrusted until validated.
- Whole-file generation is preferred over partial patches.
- Every generated artifact must be traceable to the context package and the approved contracts.

## Current Scope Boundary

{self.pipeline_config.get("scopeBoundary", "Only the configured reference module is in scope.")}
"""

    def _generation_context(self, warnings: list[dict[str, str]]) -> str:
        status = self.status_from(warnings, [])
        return f"""# Generation Context

## Objective

Use this package to support downstream planning and generation for the Pipeline Management reference module.

## Required Downstream Outputs

The downstream stages should be able to derive:

- agile artifacts,
- database schema,
- backend services and APIs,
- frontend screens,
- validation rules,
- tests,
- reports,
- implementation verification criteria.

## Input Authority

- Functional authority: SRS extract in `{self.group("contextFiles")["moduleContext"]}`.
- Technical authority: ATS extract in `{self.group("contextFiles")["architectureContext"]}`.
- Scope authority: this context package manifest and validation report.

## Validation Status

`{status}`
"""

    def _source_index_context(self) -> str:
        return "# Source Index\n\nSee `provenance.json` for checksums and file classifications. The primary source files are the approved module SRS and ATS.\n"

    def _open_questions_context(self, warnings: list[dict[str, str]]) -> str:
        if not warnings:
            return "# Open Questions\n\nNo open questions were detected for this context-engineering run.\n"
        lines = ["# Open Questions", "", "## Non-Blocking Warnings", ""]
        lines.extend(f"- `{warning['code']}`: {warning['message']}" for warning in warnings)
        return "\n".join(lines) + "\n"

    def _build_manifest(self, project: dict[str, Any], validation_status: str, context_output_names: list[str]) -> dict[str, Any]:
        return {
            "package_id": self.resolve_placeholders(self.group("output")["contextPackageId"]),
            "package_type": "module_reference_context",
            "pipeline": self.pipeline_id(),
            "pipeline_version": self.pipeline_config.get("pipelineVersion"),
            "created_at_utc": utc_now_iso(),
            "project_id": self.project_id(),
            "project_name": project.get("name", self.project_id()),
            "module_id": self.module_id(),
            "source_input_root": self.to_project_relative_path(self.CAutomation_root() / "projects" / self.project_id() / "input"),
            "validation_status": validation_status,
            "included_context_files": context_output_names,
            "structured_outputs": list(self.group("structuredFiles").values()),
            "downstream_consumers": self.pipeline_config.get("downstreamConsumers", []),
        }

    def _build_provenance(self, source_files: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "package_id": self.resolve_placeholders(self.group("output")["contextPackageId"]),
            "created_at_utc": utc_now_iso(),
            "producer": f"{self.pipeline_id()}.{self.pipeline_config.get('pipelineVersion')}",
            "source_files": source_files,
            "transformations": [
                "validated required input paths",
                "extracted DOCX text and tables into deterministic Markdown",
                "assembled ordered context files",
                "recorded source checksums and validation results",
            ],
            "excluded_inputs": [
                {
                    "category": "arbitrary_repository_files",
                    "reason": "Context Engineering consumes only configured project metadata and approved module SRS/ATS.",
                }
            ],
        }

    def _write_text_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        self.generated_files.append(self.to_project_relative_path(path))

    def _write_json_package_file(self, package_dir: Path, file_name: str, payload: dict[str, Any]) -> None:
        path = package_dir / file_name
        write_json_file(path, payload)
        self.generated_files.append(self.to_project_relative_path(path))


if __name__ == "__main__":
    BuildContextPackageTask().run()
