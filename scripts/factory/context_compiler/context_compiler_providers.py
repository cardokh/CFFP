from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.context_compiler.context_compiler_contracts import (
    ContextItem,
    ProviderResult,
)


TEXT_EXTENSIONS = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}


class ApprovedDocumentSetProvider:
    """Collects approved task documents in an explicit configured order."""

    provider_id = "approved-document-set"

    def collect(self, project_root: Path, config: dict) -> ProviderResult:
        document_root = _resolve_project_path(project_root, config["documentRoot"])
        approved_paths = config.get("approvedDocuments", [])
        include_extensions = set(config.get("includeExtensions", []))
        ignore_path_parts = set(config.get("ignorePathParts", []))

        approved_relative_paths = set(approved_paths)
        included_items = []
        excluded_inputs = []
        findings = []

        for relative_path in approved_paths:
            absolute_path = document_root / relative_path
            source_path = _to_project_relative_path(project_root, absolute_path)

            if not absolute_path.exists():
                findings.append(
                    _finding(
                        status="FAILED",
                        severity="ERROR",
                        message="Approved document is missing.",
                        path=source_path,
                    )
                )
                continue

            if not absolute_path.is_file():
                findings.append(
                    _finding(
                        status="FAILED",
                        severity="ERROR",
                        message="Approved document path is not a file.",
                        path=source_path,
                    )
                )
                continue

            if include_extensions and absolute_path.suffix not in include_extensions:
                excluded_inputs.append(
                    _excluded(
                        path=source_path,
                        reason="File extension is not approved for document context.",
                    )
                )
                continue

            content = _read_text(absolute_path)
            included_items.append(
                ContextItem(
                    provider_id=self.provider_id,
                    title=relative_path,
                    source_path=source_path,
                    content=content,
                    metadata=_file_metadata(absolute_path, content),
                )
            )

        for candidate_path in sorted(document_root.rglob("*")):
            if not candidate_path.is_file():
                continue
            if any(part in ignore_path_parts for part in candidate_path.relative_to(document_root).parts):
                continue

            relative_to_document_root = _to_posix(candidate_path.relative_to(document_root))
            source_path = _to_project_relative_path(project_root, candidate_path)

            if relative_to_document_root in approved_relative_paths:
                continue

            if include_extensions and candidate_path.suffix not in include_extensions:
                reason = "File extension is outside compiler scope."
            else:
                reason = "File is not part of the approved document set."

            excluded_inputs.append(
                _excluded(
                    path=source_path,
                    reason=reason,
                )
            )

        return ProviderResult(
            provider_id=self.provider_id,
            included_items=included_items,
            excluded_inputs=excluded_inputs,
            findings=findings,
            summary={
                "documentRoot": _to_project_relative_path(project_root, document_root),
                "approvedDocumentCount": len(approved_paths),
                "includedDocumentCount": len(included_items),
                "excludedInputCount": len(excluded_inputs),
            },
        )


class GoldenReferenceProvider:
    """Collects golden reference files from configured reference groups."""

    provider_id = "golden-reference"

    def collect(self, project_root: Path, config: dict) -> ProviderResult:
        included_items = []
        excluded_inputs = []
        findings = []
        reference_groups = config.get("referenceGroups", [])

        for group in reference_groups:
            group_id = group.get("id", "unnamed-reference-group")
            for relative_path in group.get("paths", []):
                absolute_path = _resolve_project_path(project_root, relative_path)
                source_path = _to_project_relative_path(project_root, absolute_path)

                if not absolute_path.exists():
                    findings.append(
                        _finding(
                            status="FAILED",
                            severity="ERROR",
                            message=f"Golden reference path is missing for group '{group_id}'.",
                            path=source_path,
                        )
                    )
                    continue

                if absolute_path.is_dir():
                    files = _collect_files(absolute_path, group.get("includeExtensions", list(TEXT_EXTENSIONS)))
                else:
                    files = [absolute_path]

                for file_path in files:
                    if file_path.suffix not in set(group.get("includeExtensions", list(TEXT_EXTENSIONS))):
                        excluded_inputs.append(
                            _excluded(
                                path=_to_project_relative_path(project_root, file_path),
                                reason=f"Golden reference file extension is outside group '{group_id}' scope.",
                            )
                        )
                        continue

                    content = _read_text(file_path)
                    included_items.append(
                        ContextItem(
                            provider_id=self.provider_id,
                            title=f"{group_id}: {_to_project_relative_path(project_root, file_path)}",
                            source_path=_to_project_relative_path(project_root, file_path),
                            content=content,
                            metadata={
                                **_file_metadata(file_path, content),
                                "referenceGroup": group_id,
                            },
                        )
                    )

        included_items.sort(key=lambda item: item.source_path)

        return ProviderResult(
            provider_id=self.provider_id,
            included_items=included_items,
            excluded_inputs=excluded_inputs,
            findings=findings,
            summary={
                "referenceGroupCount": len(reference_groups),
                "includedReferenceFileCount": len(included_items),
                "excludedInputCount": len(excluded_inputs),
            },
        )


class RepositoryInspectionProvider:
    """Inspects repository structure and reports deterministic project facts."""

    provider_id = "repository-inspection"

    def collect(self, project_root: Path, config: dict) -> ProviderResult:
        inspection_roots = config.get("inspectionRoots", [])
        ignore_parts = set(config.get("ignorePathParts", []))
        include_extensions = set(config.get("includeExtensions", list(TEXT_EXTENSIONS)))
        max_files_per_root = int(config.get("maxFilesPerRoot", 500))

        inspected_roots = []
        file_entries = []
        findings = []

        for relative_root in inspection_roots:
            absolute_root = _resolve_project_path(project_root, relative_root)
            root_entry = {
                "path": _to_project_relative_path(project_root, absolute_root),
                "exists": absolute_root.exists(),
                "fileCount": 0,
            }

            if not absolute_root.exists():
                findings.append(
                    _finding(
                        status="FAILED",
                        severity="ERROR",
                        message="Repository inspection root is missing.",
                        path=root_entry["path"],
                    )
                )
                inspected_roots.append(root_entry)
                continue

            files = []
            if absolute_root.is_file():
                files = [absolute_root]
            else:
                for candidate_path in sorted(absolute_root.rglob("*")):
                    if not candidate_path.is_file():
                        continue
                    if any(part in ignore_parts for part in candidate_path.parts):
                        continue
                    if candidate_path.suffix not in include_extensions:
                        continue
                    files.append(candidate_path)

            for file_path in files[:max_files_per_root]:
                content = _read_text(file_path)
                file_entries.append(
                    {
                        "path": _to_project_relative_path(project_root, file_path),
                        "extension": file_path.suffix,
                        "sizeBytes": file_path.stat().st_size,
                        "lineCount": _line_count(content),
                        "sha256": _sha256(content),
                    }
                )

            root_entry["fileCount"] = len(files)
            root_entry["reportedFileCount"] = min(len(files), max_files_per_root)
            inspected_roots.append(root_entry)

        summary_content = _render_repository_summary(inspected_roots, file_entries)

        included_items = [
            ContextItem(
                provider_id=self.provider_id,
                title="Repository Inspection Summary",
                source_path="repository-runtime-inspection",
                content=summary_content,
                metadata={
                    "inspectedRootCount": len(inspected_roots),
                    "reportedFileCount": len(file_entries),
                },
            )
        ]

        return ProviderResult(
            provider_id=self.provider_id,
            included_items=included_items,
            excluded_inputs=[],
            findings=findings,
            summary={
                "inspectedRoots": inspected_roots,
                "reportedFileCount": len(file_entries),
            },
        )


def _render_repository_summary(inspected_roots: list[dict], file_entries: list[dict]) -> str:
    lines = [
        "# Repository Inspection Summary",
        "",
        "## Inspected Roots",
        "",
    ]

    for root in inspected_roots:
        lines.append(
            f"- `{root['path']}`: exists={str(root['exists']).lower()}, files={root['fileCount']}, reported={root.get('reportedFileCount', 0)}"
        )

    lines.extend(["", "## Reported Files", ""])

    for entry in sorted(file_entries, key=lambda item: item["path"]):
        lines.append(
            f"- `{entry['path']}` | ext={entry['extension']} | lines={entry['lineCount']} | bytes={entry['sizeBytes']} | sha256={entry['sha256']}"
        )

    lines.append("")
    return "\n".join(lines)


def _collect_files(root: Path, include_extensions: list[str]) -> list[Path]:
    extensions = set(include_extensions)
    return [
        candidate_path
        for candidate_path in sorted(root.rglob("*"))
        if candidate_path.is_file() and candidate_path.suffix in extensions
    ]


def _read_text(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _file_metadata(file_path: Path, content: str) -> dict:
    return {
        "sizeBytes": file_path.stat().st_size,
        "lineCount": _line_count(content),
        "sha256": _sha256(content),
    }


def _line_count(content: str) -> int:
    if content == "":
        return 0
    return content.count("\n") + (0 if content.endswith("\n") else 1)


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _resolve_project_path(project_root: Path, relative_path: str) -> Path:
    path = (project_root / relative_path).resolve()
    if project_root.resolve() not in path.parents and path != project_root.resolve():
        raise ValueError(f"Configured path escapes project root: {relative_path}")
    return path


def _to_project_relative_path(project_root: Path, file_path: Path) -> str:
    return _to_posix(file_path.resolve().relative_to(project_root.resolve()))


def _to_posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def _finding(status: str, severity: str, message: str, path: str) -> dict:
    return {
        "status": status,
        "severity": severity,
        "message": message,
        "path": path,
    }


def _excluded(path: str, reason: str) -> dict:
    return {
        "path": path,
        "reason": reason,
    }
