"""Run CAutomation Pipeline 01: Context Engineering.

This executable MVP reads the approved Pipeline Management module contracts and
produces a deterministic, traceable context package for downstream planning and
generation stages.

Usage from the repository root:

    python cautomation/ai_engine/pipelines/01_context_engineering/scripts/run_context_engineering.py \
        --cautomation-root cautomation \
        --project cffp \
        --module pipeline_management
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SHARED_SCRIPTS = SCRIPT_DIR.parents[1] / "00_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from docx_reader import DocxReadError, read_docx_as_markdown  # noqa: E402
from file_contracts import read_text, sha256_file, write_json, write_text  # noqa: E402

PIPELINE_VERSION = "01_context_engineering.mvp-001"
SRS_FILENAME = "Software_Requirements_Specification.docx"
ATS_FILENAME = "Architecture_and_Technical_Specification.docx"


class ContextEngineeringError(RuntimeError):
    """Raised when context package creation must stop."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CAutomation Context Engineering pipeline.")
    parser.add_argument("--cautomation-root", default="cautomation", help="Path to the cautomation folder.")
    parser.add_argument("--project", default="cffp", help="Project identifier under cautomation/projects/.")
    parser.add_argument("--module", default="pipeline_management", help="Module identifier under project input modules.")
    parser.add_argument(
        "--output-root",
        default=None,
        help="Optional output root. Defaults to projects/<project>/output/context_packages/.",
    )
    parser.add_argument("--clean", action="store_true", help="Remove existing package files before writing.")
    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_project(cautomation_root: Path, project_id: str) -> dict[str, Any]:
    project_file = cautomation_root / "projects" / project_id / "project.json"
    if not project_file.exists():
        raise ContextEngineeringError(f"Missing project configuration: {project_file}")
    return json.loads(project_file.read_text(encoding="utf-8"))


def collect_platform_sources(cautomation_root: Path) -> list[dict[str, Any]]:
    relative_paths = [
        "README.md",
        "ai_engine/README.md",
        "ai_engine/pipelines/README.md",
        "ai_engine/pipelines/01_context_engineering/README.md",
        "ai_engine/pipelines/01_context_engineering/input_contract.md",
        "ai_engine/pipelines/01_context_engineering/context_contract.md",
        "ai_engine/pipelines/01_context_engineering/output_contract.md",
        "ai_engine/pipelines/01_context_engineering/validation_rules.md",
    ]
    sources: list[dict[str, Any]] = []
    for relative in relative_paths:
        path = cautomation_root / relative
        if path.exists():
            sources.append(source_record(cautomation_root, path, "platform_contract", "markdown"))
    return sources


def source_record(root: Path, path: Path, category: str, file_type: str) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)).replace("\\", "/"),
        "category": category,
        "file_type": file_type,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def read_module_contracts(cautomation_root: Path, project_id: str, module_id: str) -> tuple[dict[str, str], list[dict[str, Any]]]:
    module_root = cautomation_root / "projects" / project_id / "input" / "modules" / module_id
    srs_path = module_root / SRS_FILENAME
    ats_path = module_root / ATS_FILENAME

    missing = [str(p) for p in (srs_path, ats_path) if not p.exists()]
    if missing:
        raise ContextEngineeringError("Missing required module contract(s): " + ", ".join(missing))

    try:
        srs_text = read_docx_as_markdown(srs_path)
        ats_text = read_docx_as_markdown(ats_path)
    except DocxReadError as exc:
        raise ContextEngineeringError(str(exc)) from exc

    documents = {
        "srs_markdown": srs_text,
        "ats_markdown": ats_text,
    }
    sources = [
        source_record(cautomation_root, srs_path, "module_srs", "docx"),
        source_record(cautomation_root, ats_path, "module_ats", "docx"),
    ]
    return documents, sources


def validate_inputs(cautomation_root: Path, project_id: str, module_id: str) -> dict[str, Any]:
    project_input = cautomation_root / "projects" / project_id / "input"
    module_root = project_input / "modules" / module_id
    client_root = project_input / "client"
    engineering_root = project_input / "engineering"

    checks: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    def check(name: str, path: Path, blocking: bool = True) -> None:
        passed = path.exists()
        checks.append({"name": name, "path": str(path), "passed": passed, "blocking": blocking})
        if not passed and blocking:
            errors.append({"code": name, "message": f"Required path missing: {path}"})

    check("cautomation_root_exists", cautomation_root)
    check("project_input_exists", project_input)
    check("module_root_exists", module_root)
    check("module_srs_exists", module_root / SRS_FILENAME)
    check("module_ats_exists", module_root / ATS_FILENAME)

    client_docs = [p for p in client_root.glob("*.*") if p.name != ".gitkeep"] if client_root.exists() else []
    engineering_docs = [p for p in engineering_root.glob("*.*") if p.name != ".gitkeep"] if engineering_root.exists() else []

    if not client_docs:
        warnings.append(
            {
                "code": "project_client_contracts_missing",
                "message": "No project-level client documents are present. This run is valid only as a module-reference context package.",
            }
        )
    if not engineering_docs:
        warnings.append(
            {
                "code": "project_engineering_contracts_missing",
                "message": "No project-level engineering documents are present. Module ATS is used as the implementation contract for this reference run.",
            }
        )

    return {
        "status": "FAILED" if errors else "PASSED_WITH_WARNINGS" if warnings else "PASSED",
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def make_package_id(project_id: str, module_id: str) -> str:
    return f"{project_id}_{module_id}_context_package"


def package_dir_for(cautomation_root: Path, output_root_arg: str | None, project_id: str, module_id: str) -> Path:
    output_root = Path(output_root_arg) if output_root_arg else cautomation_root / "projects" / project_id / "output" / "context_packages"
    if not output_root.is_absolute():
        output_root = cautomation_root / output_root
    return output_root / make_package_id(project_id, module_id)


def build_markdown_outputs(project: dict[str, Any], project_id: str, module_id: str, docs: dict[str, str], validation: dict[str, Any]) -> dict[str, str]:
    project_name = project.get("name", project_id)
    project_context = f"""# Project Context

## Project Identity

- Project ID: `{project_id}`
- Project Name: `{project_name}`
- Reference Module: `{module_id}`

## Current Delivery Focus

The current automation-package reference project is the Pipeline Management module. The Context Engineering pipeline must prepare deterministic context from the approved module SRS and ATS without expanding scope to unrelated modules or project-level design work.

## Project-Level Input Status

Project-level client and engineering documents are intentionally deferred in this iteration. Their absence is recorded as a warning, not as a blocker, because this run is scoped to the approved Pipeline Management module contracts.
"""

    module_context = f"""# Module Context

## Scope

- Project: `{project_id}`
- Module: `{module_id}`
- Source of functional truth: `{SRS_FILENAME}`
- Source of technical truth: `{ATS_FILENAME}`

## Software Requirements Specification Extract

{docs['srs_markdown']}
"""

    architecture_context = f"""# Architecture Context

## Source Rule

The ATS implements the approved SRS. The ATS must not introduce unrelated business requirements.

## Architecture and Technical Specification Extract

{docs['ats_markdown']}
"""

    constraints = """# Constraints Context

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

Only the Pipeline Management reference module is in scope for this package.
"""

    global_context = """# Global Context

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

The first deliverable is the executable CAutomation package, validated through the Pipeline Management reference module.
"""

    generation_context = f"""# Generation Context

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

- Functional authority: SRS extract in `module-context.md`.
- Technical authority: ATS extract in `architecture-context.md`.
- Scope authority: this context package manifest and validation report.

## Validation Status

`{validation['status']}`
"""

    source_index = """# Source Index

See `provenance.json` for checksums and file classifications. The primary source files are the approved module SRS and ATS.
"""

    open_questions = "# Open Questions\n\n"
    if validation["warnings"]:
        open_questions += "## Non-Blocking Warnings\n\n"
        for warning in validation["warnings"]:
            open_questions += f"- `{warning['code']}`: {warning['message']}\n"
    else:
        open_questions += "No open questions were detected for this context-engineering run.\n"

    return {
        "global-context.md": global_context,
        "project-context.md": project_context,
        "module-context.md": module_context,
        "architecture-context.md": architecture_context,
        "constraints-context.md": constraints,
        "generation-context.md": generation_context,
        "source_index.md": source_index,
        "open_questions.md": open_questions,
    }


def run() -> int:
    args = parse_args()
    cautomation_root = Path(args.cautomation_root).resolve()
    project_id = args.project
    module_id = args.module

    validation = validate_inputs(cautomation_root, project_id, module_id)
    if validation["errors"]:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 2

    project = load_project(cautomation_root, project_id)
    docs, module_sources = read_module_contracts(cautomation_root, project_id, module_id)
    platform_sources = collect_platform_sources(cautomation_root)
    package_dir = package_dir_for(cautomation_root, args.output_root, project_id, module_id)

    if args.clean and package_dir.exists():
        for child in sorted(package_dir.iterdir()):
            if child.is_file():
                child.unlink()

    created_at = utc_now_iso()
    package_id = make_package_id(project_id, module_id)
    markdown_outputs = build_markdown_outputs(project, project_id, module_id, docs, validation)

    for filename, content in markdown_outputs.items():
        write_text(package_dir / filename, content)

    source_files = module_sources + platform_sources
    manifest = {
        "package_id": package_id,
        "package_type": "module_reference_context",
        "pipeline": "01_context_engineering",
        "pipeline_version": PIPELINE_VERSION,
        "created_at_utc": created_at,
        "project_id": project_id,
        "project_name": project.get("name", project_id),
        "module_id": module_id,
        "source_input_root": f"projects/{project_id}/input",
        "validation_status": validation["status"],
        "included_context_files": sorted(markdown_outputs.keys()),
        "structured_outputs": ["manifest.json", "provenance.json", "validation_report.json"],
        "downstream_consumers": [
            "02_planning",
            "03_generation/db",
            "03_generation/backend",
            "03_generation/frontend",
            "03_generation/testing",
            "03_generation/deployment",
            "04_validation",
        ],
    }
    provenance = {
        "package_id": package_id,
        "created_at_utc": created_at,
        "producer": PIPELINE_VERSION,
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
                "reason": "Context Engineering MVP only consumes platform contracts, project metadata, and approved module SRS/ATS.",
            }
        ],
    }

    write_json(package_dir / "manifest.json", manifest)
    write_json(package_dir / "provenance.json", provenance)
    write_json(package_dir / "validation_report.json", validation)

    print(json.dumps({"status": validation["status"], "package_dir": str(package_dir)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
