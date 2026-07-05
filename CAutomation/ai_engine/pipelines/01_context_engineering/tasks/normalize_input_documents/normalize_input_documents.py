"""Task 02 - Normalize Input Documents for Pipeline 01 Context Engineering."""

from __future__ import annotations

import json
import re
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
from scripts.shared.script_console_utils import print_failed, print_passed, print_warning  # noqa: E402

from document_normalizers import DocumentNormalizerRegistry  # noqa: E402


class NormalizeInputDocumentsTask(ContextEngineeringSupportMixin, BaseScript):
    """Normalizes source input contracts into the canonical downstream input format."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.pipeline_config: dict[str, Any] = self.load_pipeline_config()
        self.document_normalizers = DocumentNormalizerRegistry()

    def run(self) -> None:
        started = time.perf_counter()
        started_at_utc = utc_now_iso()
        checks: list[dict[str, Any]] = []
        warnings: list[dict[str, str]] = []
        errors: list[dict[str, str]] = []
        normalized_documents: dict[str, dict[str, Any]] = {}
        generated_files: list[str] = []
        try:
            srs_path, ats_path = self.contract_paths()
            required_paths = {
                "CAutomation_root_exists": self.CAutomation_root(),
                "project_config_exists": self.project_config_path(),
                "module_input_root_exists": self.module_input_root(),
                "module_srs_exists": srs_path,
                "module_ats_exists": ats_path,
            }
            for name, path in required_paths.items():
                self._record_path_check(name, path, checks, errors)

            validation_config = self.group("validation")
            quality_gate = validation_config.get("inputQualityGate", {})
            if isinstance(quality_gate, dict) and quality_gate.get("enabled", True) is True:
                self._normalize_manual_input_documents(quality_gate, checks, errors, normalized_documents)
                self._validate_cross_document_rules(quality_gate, checks, errors, normalized_documents)

            project_input = self.project_input_root()
            if validation_config.get("warnWhenProjectClientContractsMissing", True) is True:
                self._warn_when_no_contract_files(
                    root=project_input / "client",
                    warning_code="project_client_contracts_missing",
                    message="No project-level client contracts are present. This run is valid as a module-reference context package.",
                    warnings=warnings,
                )
            if validation_config.get("warnWhenProjectEngineeringContractsMissing", True) is True:
                self._warn_when_no_contract_files(
                    root=project_input / "engineering",
                    warning_code="project_engineering_contracts_missing",
                    message="No project-level engineering contracts are present. Module ATS is used as the implementation contract for this reference run.",
                    warnings=warnings,
                )

            status = self.status_from(warnings, errors)
            normalized_root = self.normalized_input_root()
            manifest_path = normalized_root / "normalization_manifest.json"
            normalization_report_path = normalized_root / "normalization_report.json"
            if not errors:
                generated_files = self._write_normalized_documents(normalized_documents, normalized_root)
                manifest = self._build_manifest(normalized_documents, generated_files)
                manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
                generated_files.append(self.to_project_relative_path(manifest_path))

            state_payload = {
                "status": status,
                "gateType": "hard_normalized_input_quality_gate",
                "gateDecision": "REJECTED" if errors else "ACCEPTED",
                "normalizedInputRoot": self.to_project_relative_path(normalized_root),
                "normalizationManifestPath": self.to_project_relative_path(manifest_path) if not errors else None,
                "normalizationReportPath": self.to_project_relative_path(normalization_report_path),
                "documents": {
                    document_id: {
                        "sourcePath": data["sourcePath"],
                        "sourceFormat": data["sourceFormat"],
                        "normalizedPath": data.get("normalizedPath"),
                        "characterCount": data["characterCount"],
                    }
                    for document_id, data in normalized_documents.items()
                },
                "checks": checks,
                "warnings": warnings,
                "errors": errors,
                "generatedFiles": generated_files,
            }
            self.write_state_json(self.pipeline_task_state_file("normalize_input_documents"), state_payload)
            normalization_report_path.parent.mkdir(parents=True, exist_ok=True)
            normalization_report_path.write_text(json.dumps(state_payload, indent=2), encoding="utf-8")
            if not errors and self.to_project_relative_path(normalization_report_path) not in generated_files:
                generated_files.append(self.to_project_relative_path(normalization_report_path))

            report = self.base_report(status, started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"normalization": state_payload})
            report_path = self.write_task_report(report)
            if status == "FAILED":
                print_failed(f"normalize_input_documents FAILED; report {self.to_project_relative_path(report_path)}")
                sys.exit(1)
            if status == "PASSED_WITH_WARNINGS":
                print_warning(f"normalize_input_documents PASSED_WITH_WARNINGS; report {self.to_project_relative_path(report_path)}")
            else:
                print_passed(f"normalize_input_documents PASSED; report {self.to_project_relative_path(report_path)}")
        except Exception as exc:  # noqa: BLE001
            report = self.base_report("FAILED", started_at_utc, round(time.perf_counter() - started, 3))
            report.update({"errors": [{"code": "unexpected_error", "message": str(exc)}], "exceptionType": type(exc).__name__})
            report_path = self.write_task_report(report)
            print_failed(f"normalize_input_documents FAILED; report {self.to_project_relative_path(report_path)}")
            raise

    def _record_path_check(self, name: str, path: Path, checks: list[dict[str, Any]], errors: list[dict[str, str]]) -> None:
        passed = path.exists()
        checks.append({
            "name": name,
            "category": "structural_completeness",
            "path": self.to_project_relative_path(path) if path.exists() else str(path),
            "passed": passed,
            "blocking": True,
        })
        if not passed:
            errors.append({"code": name, "message": f"Required path missing: {path}"})

    def _normalize_manual_input_documents(
        self,
        quality_gate: dict[str, Any],
        checks: list[dict[str, Any]],
        errors: list[dict[str, str]],
        normalized_documents: dict[str, dict[str, Any]],
    ) -> None:
        input_config = self.group("input")
        documents = quality_gate.get("manualInputDocuments", [])
        if not isinstance(documents, list):
            errors.append({"code": "invalid_input_quality_gate_config", "message": "inputQualityGate.manualInputDocuments must be an array."})
            return

        configured_formats = [str(value).lower().lstrip(".") for value in quality_gate.get("supportedSourceFormats", self.document_normalizers.supported_formats()) if str(value).strip()]
        supported_formats = [source_format for source_format in configured_formats if self.document_normalizers.supports(source_format)]
        minimum_characters = int(quality_gate.get("minimumExtractedCharacters", 1))
        forbidden_tokens = [str(token) for token in quality_gate.get("forbiddenPlaceholderTokens", []) if str(token).strip()]
        hierarchy_terms = [str(term) for term in quality_gate.get("requiredHierarchyTerms", []) if str(term).strip()]

        for document in documents:
            if not isinstance(document, dict):
                continue
            document_id = str(document.get("documentId", "")).strip()
            file_name_key = str(document.get("fileNameKey", "")).strip()
            display_name = str(document.get("displayName", document_id)).strip() or document_id
            normalized_file_name = str(document.get("normalizedFileName", f"{document_id}.md")).strip() or f"{document_id}.md"
            file_name = input_config.get(file_name_key)
            if not document_id or not isinstance(file_name, str) or not file_name.strip():
                errors.append({"code": "invalid_document_profile", "message": f"Invalid manual input document profile: {document}"})
                continue
            path = self.module_input_root() / file_name
            source_format = path.suffix.lower().lstrip(".")
            self._record_supported_format_check(document_id, display_name, path, source_format, supported_formats, checks, errors)
            text = self._normalize_document_text(document_id, display_name, path, checks, errors)
            normalized_documents[document_id] = {
                "documentId": document_id,
                "displayName": display_name,
                "sourcePath": self.to_project_relative_path(path),
                "sourceFormat": source_format,
                "normalizedFileName": normalized_file_name,
                "markdown": text,
                "characterCount": len(text),
            }
            if not text:
                continue
            self._record_text_length_check(document_id, display_name, text, minimum_characters, checks, errors)
            self._record_required_terms_check(document_id, display_name, text, document.get("requiredTerms", []), "template_section_coverage", checks, errors)
            self._record_required_terms_check(document_id, display_name, text, hierarchy_terms, "context_path_alignment", checks, errors)
            self._record_forbidden_tokens_check(document_id, display_name, text, forbidden_tokens, checks, errors)

    def _record_supported_format_check(
        self,
        document_id: str,
        display_name: str,
        path: Path,
        source_format: str,
        supported_formats: list[str],
        checks: list[dict[str, Any]],
        errors: list[dict[str, str]],
    ) -> None:
        passed = bool(source_format) and source_format in supported_formats
        checks.append({
            "name": f"{document_id}_supported_source_format",
            "category": "source_format_eligibility",
            "path": self.to_project_relative_path(path) if path.exists() else str(path),
            "sourceFormat": source_format,
            "supportedFormats": supported_formats,
            "passed": passed,
            "blocking": True,
        })
        if not passed:
            errors.append({"code": f"{document_id}_unsupported_source_format", "message": f"{display_name} has unsupported source format: {source_format or '<none>'}."})

    def _normalize_document_text(self, document_id: str, display_name: str, path: Path, checks: list[dict[str, Any]], errors: list[dict[str, str]]) -> str:
        if not path.exists():
            return ""
        try:
            result = self.document_normalizers.normalize(path)
            text = result.markdown.strip()
        except Exception as exc:  # noqa: BLE001
            checks.append({
                "name": f"{document_id}_readable_source_document",
                "category": "structural_integrity",
                "path": self.to_project_relative_path(path),
                "passed": False,
                "blocking": True,
            })
            errors.append({"code": f"{document_id}_unreadable_source_document", "message": f"{display_name} could not be read and normalized: {exc}"})
            return ""
        passed = bool(text)
        checks.append({
            "name": f"{document_id}_readable_source_document",
            "category": "structural_integrity",
            "path": self.to_project_relative_path(path),
            "passed": passed,
            "blocking": True,
        })
        if not passed:
            errors.append({"code": f"{document_id}_empty_document", "message": f"{display_name} does not contain extractable text."})
        return text

    def _write_normalized_documents(self, normalized_documents: dict[str, dict[str, Any]], normalized_root: Path) -> list[str]:
        normalized_root.mkdir(parents=True, exist_ok=True)
        generated_files: list[str] = []
        for data in normalized_documents.values():
            output_path = normalized_root / data["normalizedFileName"]
            output_path.write_text(data["markdown"].strip() + "\n", encoding="utf-8", newline="\n")
            data["normalizedPath"] = self.to_project_relative_path(output_path)
            generated_files.append(data["normalizedPath"])
        return generated_files

    def _build_manifest(self, normalized_documents: dict[str, dict[str, Any]], generated_files: list[str]) -> dict[str, Any]:
        sources = []
        for data in normalized_documents.values():
            source_path = self.CAutomation_root().parent / data["sourcePath"]
            sources.append(source_record(self, source_path, data["documentId"], data["sourceFormat"]))
        return {
            "manifestType": "normalized_input_manifest",
            "pipelineId": self.pipeline_id(),
            "projectId": self.project_id(),
            "moduleId": self.module_id(),
            "normalizedInputRoot": self.to_project_relative_path(self.normalized_input_root()),
            "documents": [
                {
                    "documentId": data["documentId"],
                    "displayName": data["displayName"],
                    "sourcePath": data["sourcePath"],
                    "sourceFormat": data["sourceFormat"],
                    "normalizedPath": data.get("normalizedPath"),
                    "characterCount": data["characterCount"],
                }
                for data in normalized_documents.values()
            ],
            "sourceFiles": sources,
            "generatedFiles": generated_files,
        }

    def _record_text_length_check(self, document_id: str, display_name: str, text: str, minimum_characters: int, checks: list[dict[str, Any]], errors: list[dict[str, str]]) -> None:
        passed = len(text) >= minimum_characters
        checks.append({"name": f"{document_id}_minimum_content_length", "category": "structural_completeness", "minimumCharacters": minimum_characters, "actualCharacters": len(text), "passed": passed, "blocking": True})
        if not passed:
            errors.append({"code": f"{document_id}_insufficient_content", "message": f"{display_name} is below the minimum extracted content length."})

    def _record_required_terms_check(self, document_id: str, display_name: str, text: str, terms: Any, category: str, checks: list[dict[str, Any]], errors: list[dict[str, str]]) -> None:
        if not isinstance(terms, list):
            errors.append({"code": f"{document_id}_invalid_required_terms", "message": f"Required terms for {display_name} must be an array."})
            return
        for term in [str(value) for value in terms if str(value).strip()]:
            passed = self._contains_term(text, term)
            checks.append({"name": f"{document_id}_contains_{self._safe_check_name(term)}", "category": category, "term": term, "passed": passed, "blocking": True})
            if not passed:
                errors.append({"code": f"{document_id}_missing_required_term", "message": f"{display_name} is missing required template/context term: {term}"})

    def _record_forbidden_tokens_check(self, document_id: str, display_name: str, text: str, tokens: list[str], checks: list[dict[str, Any]], errors: list[dict[str, str]]) -> None:
        for token in tokens:
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            passed = pattern.search(text) is None
            checks.append({"name": f"{document_id}_no_{self._safe_check_name(token)}", "category": "ambiguity_and_gap_minimization", "token": token, "passed": passed, "blocking": True})
            if not passed:
                errors.append({"code": f"{document_id}_placeholder_token_found", "message": f"{display_name} contains unresolved placeholder token: {token}"})

    def _validate_cross_document_rules(self, quality_gate: dict[str, Any], checks: list[dict[str, Any]], errors: list[dict[str, str]], normalized_documents: dict[str, dict[str, Any]]) -> None:
        references = quality_gate.get("crossDocumentReferences", [])
        if not isinstance(references, list):
            errors.append({"code": "invalid_cross_document_reference_config", "message": "inputQualityGate.crossDocumentReferences must be an array."})
            return
        for rule in references:
            if not isinstance(rule, dict):
                continue
            source_document_id = str(rule.get("sourceDocumentId", "")).strip()
            required_term = str(rule.get("requiredTerm", "")).strip()
            text = str(normalized_documents.get(source_document_id, {}).get("markdown", ""))
            passed = bool(text) and self._contains_term(text, required_term)
            checks.append({"name": f"{source_document_id}_cross_references_{self._safe_check_name(required_term)}", "category": "referential_integrity", "sourceDocumentId": source_document_id, "requiredTerm": required_term, "passed": passed, "blocking": True})
            if not passed:
                errors.append({"code": "missing_cross_document_reference", "message": f"Document '{source_document_id}' must reference '{required_term}'."})

    def _warn_when_no_contract_files(self, root: Path, warning_code: str, message: str, warnings: list[dict[str, str]]) -> None:
        files = [path for path in root.glob("*.*") if path.name != ".gitkeep"] if root.exists() else []
        if not files:
            warnings.append({"code": warning_code, "message": message})

    def _contains_term(self, text: str, term: str) -> bool:
        return re.search(re.escape(term), text, re.IGNORECASE) is not None

    def _safe_check_name(self, value: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
        return safe or "value"


if __name__ == "__main__":
    NormalizeInputDocumentsTask().run()
