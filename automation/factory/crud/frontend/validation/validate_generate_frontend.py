"""Validate the frontend CRUD automation generator and generated Pipeline UI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def require_file(repo_root: Path, relative_path: str, errors: list[str]) -> None:
    if not (repo_root / relative_path).is_file():
        errors.append(f"Missing file: {relative_path}")


def validate_generated_output(repo_root: Path, errors: list[str]) -> None:
    expectations = {
        "frontend/static/desktop/protected/ccore/automation/pipelines/pipelines.html": [
            "shared-table ccore-pipelines-table",
            "ccorePipelinesTableBody",
            "ccorePipelinesSearchInput",
            "Create Pipeline",
            "Pipeline Name",
            "Status",
            "Created",
        ],
        "frontend/static/desktop/protected/ccore/automation/pipelines/js/pipelines.js": [
            "CCORE_API_ENDPOINTS.pipelines.list",
            "responseData.pipelines",
            "pipeline.pipelineName",
            "pipeline.pipelineStatusLabel",
            "pipeline-details.html?pipelineId=",
        ],
        "frontend/static/desktop/protected/ccore/automation/pipelines/pipeline-details.html": [
            "ccorePipelineStatusInput",
            "ccorePipelineDescriptionInput",
            "Create Pipeline",
            "Delete Pipeline",
        ],
        "frontend/static/desktop/protected/ccore/automation/pipelines/js/pipeline-details.js": [
            "CCORE_API_ENDPOINTS.pipelines.statuses",
            "pipelineStatuses",
            "postJson(CCORE_API_ENDPOINTS.pipelines.create",
            "putJson(CCORE_API_ENDPOINTS.pipelines.byId",
            "deleteJson(CCORE_API_ENDPOINTS.pipelines.byId",
        ],
        "frontend/static/shared/api-endpoints.js": [
            "pipelines: {",
            "/api/ccore/pipelines",
            "/api/ccore/pipeline-statuses",
        ],
        "frontend/static/desktop/protected/ccore/automation/automation.html": [
            "automation/pipelines/pipelines.html",
            "CCore Automation Pipelines",
        ],
    }

    for relative_path, snippets in expectations.items():
        path = repo_root / relative_path
        if not path.is_file():
            errors.append(f"Generated output missing: {relative_path}")
            continue
        content = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in content:
                errors.append(f"{relative_path} missing expected snippet: {snippet}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate frontend CRUD automation generator.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--config",
        default="automation/factory/crud/frontend/validation/config/validate_generate_frontend.json",
    )
    parser.add_argument("--include-generated-output", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    config = json.loads((repo_root / args.config).read_text(encoding="utf-8"))
    errors: list[str] = []

    for relative_path in config["required_generator_files"]:
        require_file(repo_root, relative_path, errors)
    for relative_path in config["required_golden_files"]:
        require_file(repo_root, relative_path, errors)

    if args.include_generated_output:
        validate_generated_output(repo_root, errors)

    if errors:
        print("Frontend CRUD generator validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Frontend CRUD generator validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
