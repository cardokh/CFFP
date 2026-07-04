"""CAutomation Pipeline 01 task: context_engineering.

This task follows the repository scripting infrastructure:

- it is placed under a pipeline task folder,
- it extends scripts.shared.base_script.BaseScript,
- it reads all execution settings from config/context_engineering.json,
- it writes a JSON execution report to this task's output folder,
- it writes the generated context package to the configured project output folder.

Run from the repository root:

    python cautomation/ai_engine/pipelines/01_context_engineering/tasks/context_engineering/context_engineering.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


def _configure_project_import_path() -> None:
    project_root = next(
        (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript  # noqa: E402
from scripts.shared.script_console_utils import print_failed, print_passed, print_warning  # noqa: E402
from scripts.shared.script_json_utils import read_json_file, write_json_file  # noqa: E402

_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class ContextEngineeringTask(BaseScript):
    """Creates a deterministic context package from approved SRS/ATS contracts."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.started_at_utc = self._utc_now_iso()
        self.project_id = self._required_config_string("projectId")
        self.module_id = self._required_config_string("moduleId")
        self.pipeline_id = self._required_config_string("pipelineId")
        self.task_id = self._required_config_string("taskId")
        self.task_version = self._required_config_string("taskVersion")
        self.input_config = self._required_config_group("input")
        self.output_config = self._required_config_group("output")
        self.context_files_config = self._required_config_group("contextFiles")
        self.structured_files_config = self._required_config_group("structuredFiles")
        self.validation_config = self._required_config_group("validation")
        self.cautomation_root = self._resolve_configured_project_path(self.input_config["cautomationRoot"])
        self.package_dir = self._resolve_context_package_dir()
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []
        self.checks: list[dict[str, Any]] = []
        self.generated_files: list[str] = []

    def run(self) -> None:
        started = time.perf_counter()
        try:
            self._validate_inputs()
            if self.errors:
                self._finish_failed(started)
                return

            project = self._load_project_config()
            srs_path, ats_path = self._contract_paths()
            srs_markdown = self._read_docx_as_markdown(srs_path)
            ats_markdown = self._read_docx_as_markdown(ats_path)
            self._prepare_package_dir()

            context_outputs = self._build_context_outputs(
                project=project,
                srs_markdown=srs_markdown,
                ats_markdown=ats_markdown,
            )
            for filename, content in context_outputs.items():
                self._write_text_file(self.package_dir / filename, content)

            validation_status = self._status()
            source_files = [
                self._source_record(srs_path, "module_srs", "docx"),
                self._source_record(ats_path, "module_ats", "docx"),
                self._source_record(self._project_config_path(), "project_config", "json"),
            ]
            manifest = self._build_manifest(
                project=project,
                validation_status=validation_status,
                context_output_names=sorted(context_outputs.keys()),
            )
            provenance = self._build_provenance(source_files)
            validation_report = {
                "status": validation_status,
                "checks": self.checks,
                "warnings": self.warnings,
                "errors": self.errors,
            }

            self._write_json_package_file(self.structured_files_config["manifest"], manifest)
            self._write_json_package_file(self.structured_files_config["provenance"], provenance)
            self._write_json_package_file(self.structured_files_config["validationReport"], validation_report)

            execution_report = self._build_execution_report(
                status=validation_status,
                elapsed_seconds=round(time.perf_counter() - started, 3),
                package_manifest=manifest,
            )
            report_path = self.write_json_report(execution_report)
            self._print_status(validation_status, report_path)
        except Exception as exc:  # noqa: BLE001 - execution reports must capture unexpected failures.
            self.errors.append({"code": "unexpected_error", "message": str(exc)})
            report = self._build_execution_report(
                status="FAILED",
                elapsed_seconds=round(time.perf_counter() - started, 3),
                package_manifest={},
            )
            report["exceptionType"] = type(exc).__name__
            report_path = self.write_json_report(report)
            print_failed(f"context_engineering failed; report {self.to_project_relative_path(report_path)}")
            raise

    def _finish_failed(self, started: float) -> None:
        report = self._build_execution_report(
            status="FAILED",
            elapsed_seconds=round(time.perf_counter() - started, 3),
            package_manifest={},
        )
        report_path = self.write_json_report(report)
        print_failed(f"context_engineering failed validation; report {self.to_project_relative_path(report_path)}")

    def _print_status(self, status: str, report_path: Path) -> None:
        message = (
            f"context_engineering {status}; package {self.to_project_relative_path(self.package_dir)}; "
            f"report {self.to_project_relative_path(report_path)}"
        )
        if status == "PASSED_WITH_WARNINGS":
            print_warning(message)
        elif status == "PASSED":
            print_passed(message)
        else:
            print_failed(message)

    def _required_config_string(self, key: str) -> str:
        value = self.config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Config must contain non-empty string: {key}")
        return value

    def _required_config_group(self, key: str) -> dict[str, Any]:
        value = self.config.get(key)
        if not isinstance(value, dict):
            raise ValueError(f"Config must contain object: {key}")
        return value

    def _resolve_placeholders(self, value: str) -> str:
        replacements = {
            "projectId": self.project_id,
            "moduleId": self.module_id,
            "pipelineId": self.pipeline_id,
            "taskId": self.task_id,
        }
        resolved = value
        for key, replacement in replacements.items():
            resolved = resolved.replace("{" + key + "}", replacement)
        return resolved

    def _resolve_configured_project_path(self, configured_path: str) -> Path:
        path = Path(self._resolve_placeholders(configured_path))
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def _project_config_path(self) -> Path:
        return self.cautomation_root / self._resolve_placeholders(self.input_config["projectConfigPath"])

    def _module_input_root(self) -> Path:
        return self.cautomation_root / self._resolve_placeholders(self.input_config["moduleInputPath"])

    def _contract_paths(self) -> tuple[Path, Path]:
        module_root = self._module_input_root()
        return module_root / self.input_config["srsFileName"], module_root / self.input_config["atsFileName"]

    def _resolve_context_package_dir(self) -> Path:
        package_root = self.cautomation_root / self._resolve_placeholders(self.output_config["contextPackageRoot"])
        package_id = self._resolve_placeholders(self.output_config["contextPackageId"])
        return (package_root / package_id).resolve()

    def _validate_inputs(self) -> None:
        srs_path, ats_path = self._contract_paths()
        required_paths = {
            "cautomation_root_exists": self.cautomation_root,
            "project_config_exists": self._project_config_path(),
            "module_input_root_exists": self._module_input_root(),
            "module_srs_exists": srs_path,
            "module_ats_exists": ats_path,
        }
        for name, path in required_paths.items():
            self._check_path(name, path, blocking=True)

        project_input = self.cautomation_root / "projects" / self.project_id / "input"
        client_root = project_input / "client"
        engineering_root = project_input / "engineering"
        if self.validation_config.get("warnWhenProjectClientContractsMissing", True) is True:
            self._warn_when_no_contract_files(
                root=client_root,
                warning_code="project_client_contracts_missing",
                message="No project-level client contracts are present. This run is valid as a module-reference context package.",
            )
        if self.validation_config.get("warnWhenProjectEngineeringContractsMissing", True) is True:
            self._warn_when_no_contract_files(
                root=engineering_root,
                warning_code="project_engineering_contracts_missing",
                message="No project-level engineering contracts are present. Module ATS is used as the implementation contract for this reference run.",
            )

    def _check_path(self, name: str, path: Path, blocking: bool) -> None:
        passed = path.exists()
        self.checks.append(
            {
                "name": name,
                "path": self.to_project_relative_path(path) if path.exists() else str(path),
                "passed": passed,
                "blocking": blocking,
            }
        )
        if not passed and blocking:
            self.errors.append({"code": name, "message": f"Required path missing: {path}"})

    def _warn_when_no_contract_files(self, root: Path, warning_code: str, message: str) -> None:
        files = [path for path in root.glob("*.*") if path.name != ".gitkeep"] if root.exists() else []
        if not files:
            self.warnings.append({"code": warning_code, "message": message})

    def _load_project_config(self) -> dict[str, Any]:
        return read_json_file(self._project_config_path())

    def _prepare_package_dir(self) -> None:
        if self.output_config.get("cleanPackageBeforeWrite", True) is True and self.package_dir.exists():
            shutil.rmtree(self.package_dir)
        self.package_dir.mkdir(parents=True, exist_ok=True)

    def _status(self) -> str:
        if self.errors:
            return "FAILED"
        if self.warnings:
            return "PASSED_WITH_WARNINGS"
        return "PASSED"

    def _build_context_outputs(self, project: dict[str, Any], srs_markdown: str, ats_markdown: str) -> dict[str, str]:
        project_name = str(project.get("name", self.project_id))
        return {
            self.context_files_config["globalContext"]: self._global_context(),
            self.context_files_config["projectContext"]: self._project_context(project_name),
            self.context_files_config["moduleContext"]: self._module_context(srs_markdown),
            self.context_files_config["architectureContext"]: self._architecture_context(ats_markdown),
            self.context_files_config["constraintsContext"]: self._constraints_context(),
            self.context_files_config["generationContext"]: self._generation_context(),
            self.context_files_config["sourceIndex"]: self._source_index_context(),
            self.context_files_config["openQuestions"]: self._open_questions_context(),
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

{self.config.get("firstDeliverable", "The executable CAutomation package is the first deliverable.")}
"""

    def _project_context(self, project_name: str) -> str:
        return f"""# Project Context

## Project Identity

- Project ID: `{self.project_id}`
- Project Name: `{project_name}`
- Reference Module: `{self.module_id}`

## Current Delivery Focus

The current automation-package reference project is the Pipeline Management module. The Context Engineering pipeline must prepare deterministic context from the approved module SRS and ATS without expanding scope to unrelated modules or project-level design work.

## Project-Level Input Status

Project-level client and engineering documents are intentionally deferred in this iteration. Their absence is recorded as a warning, not as a blocker, because this run is scoped to the approved Pipeline Management module contracts.
"""

    def _module_context(self, srs_markdown: str) -> str:
        return f"""# Module Context

## Scope

- Project: `{self.project_id}`
- Module: `{self.module_id}`
- Source of functional truth: `{self.input_config["srsFileName"]}`
- Source of technical truth: `{self.input_config["atsFileName"]}`

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

{self.config.get("scopeBoundary", "Only the configured reference module is in scope.")}
"""

    def _generation_context(self) -> str:
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

- Functional authority: SRS extract in `{self.context_files_config["moduleContext"]}`.
- Technical authority: ATS extract in `{self.context_files_config["architectureContext"]}`.
- Scope authority: this context package manifest and validation report.

## Validation Status

`{self._status()}`
"""

    def _source_index_context(self) -> str:
        return "# Source Index\n\nSee `provenance.json` for checksums and file classifications. The primary source files are the approved module SRS and ATS.\n"

    def _open_questions_context(self) -> str:
        if not self.warnings:
            return "# Open Questions\n\nNo open questions were detected for this context-engineering run.\n"
        lines = ["# Open Questions", "", "## Non-Blocking Warnings", ""]
        lines.extend(f"- `{warning['code']}`: {warning['message']}" for warning in self.warnings)
        return "\n".join(lines) + "\n"

    def _build_manifest(self, project: dict[str, Any], validation_status: str, context_output_names: list[str]) -> dict[str, Any]:
        return {
            "package_id": self._resolve_placeholders(self.output_config["contextPackageId"]),
            "package_type": "module_reference_context",
            "pipeline": self.pipeline_id,
            "task": self.task_id,
            "task_version": self.task_version,
            "created_at_utc": self.started_at_utc,
            "project_id": self.project_id,
            "project_name": project.get("name", self.project_id),
            "module_id": self.module_id,
            "source_input_root": self.to_project_relative_path(self.cautomation_root / "projects" / self.project_id / "input"),
            "validation_status": validation_status,
            "included_context_files": context_output_names,
            "structured_outputs": list(self.structured_files_config.values()),
            "downstream_consumers": self.config.get("downstreamConsumers", []),
        }

    def _build_provenance(self, source_files: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "package_id": self._resolve_placeholders(self.output_config["contextPackageId"]),
            "created_at_utc": self.started_at_utc,
            "producer": f"{self.pipeline_id}.{self.task_id}.{self.task_version}",
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
                    "reason": "Context Engineering task consumes only configured project metadata and approved module SRS/ATS.",
                }
            ],
        }

    def _build_execution_report(self, status: str, elapsed_seconds: float, package_manifest: dict[str, Any]) -> dict[str, Any]:
        return {
            "scriptName": self.script_name,
            "pipelineId": self.pipeline_id,
            "taskId": self.task_id,
            "taskVersion": self.task_version,
            "status": status,
            "startedAtUtc": self.started_at_utc,
            "finishedAtUtc": self._utc_now_iso(),
            "elapsedSeconds": elapsed_seconds,
            "configuration": {
                "configPath": self.to_project_relative_path(self.config_path),
                "projectId": self.project_id,
                "moduleId": self.module_id,
                "cautomationRoot": self.to_project_relative_path(self.cautomation_root),
                "contextPackageDirectory": self.to_project_relative_path(self.package_dir),
            },
            "summary": {
                "generatedFileCount": len(self.generated_files),
                "warningCount": len(self.warnings),
                "errorCount": len(self.errors),
            },
            "validation": {
                "checks": self.checks,
                "warnings": self.warnings,
                "errors": self.errors,
            },
            "generatedFiles": self.generated_files,
            "packageManifest": package_manifest,
        }

    def _write_text_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        self.generated_files.append(self.to_project_relative_path(path))

    def _write_json_package_file(self, configured_file_name: str, payload: dict[str, Any]) -> None:
        path = self.package_dir / configured_file_name
        write_json_file(path, payload)
        self.generated_files.append(self.to_project_relative_path(path))

    def _source_record(self, path: Path, category: str, file_type: str) -> dict[str, Any]:
        return {
            "path": self.to_project_relative_path(path),
            "category": category,
            "file_type": file_type,
            "sha256": self._sha256_file(path),
            "size_bytes": path.stat().st_size,
        }

    def _read_docx_as_markdown(self, path: Path) -> str:
        try:
            with ZipFile(path) as archive:
                xml_bytes = archive.read("word/document.xml")
        except (BadZipFile, KeyError) as exc:
            raise RuntimeError(f"Invalid or unsupported DOCX file: {path}") from exc

        root = ET.fromstring(xml_bytes)
        body = root.find(f"{_WORD_NS}body")
        if body is None:
            return ""

        blocks: list[str] = []
        for child in body:
            if child.tag == f"{_WORD_NS}p":
                text = self._paragraph_text(child)
                if text:
                    blocks.append(text)
            elif child.tag == f"{_WORD_NS}tbl":
                table = self._table_as_markdown(child)
                if table:
                    blocks.append(table)
        return "\n\n".join(blocks).strip() + "\n"

    def _paragraph_text(self, paragraph: ET.Element) -> str:
        return "".join(self._iter_text_nodes(paragraph)).strip()

    def _iter_text_nodes(self, element: ET.Element) -> Iterable[str]:
        for node in element.iter(f"{_WORD_NS}t"):
            if node.text:
                yield node.text

    def _table_as_markdown(self, table: ET.Element) -> str:
        rows: list[list[str]] = []
        for row in table.iter(f"{_WORD_NS}tr"):
            cells: list[str] = []
            for cell in row.iter(f"{_WORD_NS}tc"):
                paragraphs = [self._paragraph_text(p) for p in cell.iter(f"{_WORD_NS}p")]
                value = " ".join(p for p in paragraphs if p).strip()
                cells.append(value.replace("|", "\\|"))
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        max_cols = max(len(row) for row in rows)
        normalized = [row + [""] * (max_cols - len(row)) for row in rows]
        header = normalized[0]
        separator = ["---"] * max_cols
        body = normalized[1:]
        lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(separator) + " |"]
        lines.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(lines)

    def _sha256_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _utc_now_iso(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    ContextEngineeringTask().run()
