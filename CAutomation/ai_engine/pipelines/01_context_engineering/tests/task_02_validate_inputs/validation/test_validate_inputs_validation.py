from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def _cautomation_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir())


def _copy_repo(tmp_path: Path) -> Path:
    source_root = _cautomation_root()
    target_root = tmp_path / "CAutomation"
    ignore = shutil.ignore_patterns("__pycache__", ".pytest_cache", "output")
    shutil.copytree(source_root, target_root, ignore=ignore)
    return target_root


def _run_task(cautomation_root: Path) -> subprocess.CompletedProcess[str]:
    script_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/validate_inputs/validate_inputs.py"
    return subprocess.run([sys.executable, str(script_path)], cwd=cautomation_root.parent, text=True, capture_output=True, check=False)


def _pipeline_config_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/config/context_engineering_pipeline.json"


def _module_root(cautomation_root: Path) -> Path:
    return cautomation_root / "projects/pipeline_management/input/modules/pipeline_management"


def _state_path(cautomation_root: Path) -> Path:
    return cautomation_root / "ai_engine/pipelines/01_context_engineering/output/current_run/validate_inputs.json"


def _read_pipeline_config(cautomation_root: Path) -> dict:
    return json.loads(_pipeline_config_path(cautomation_root).read_text(encoding="utf-8"))


def _write_pipeline_config(cautomation_root: Path, config: dict) -> None:
    _pipeline_config_path(cautomation_root).write_text(json.dumps(config, indent=2), encoding="utf-8")


def _read_state(cautomation_root: Path) -> dict:
    return json.loads(_state_path(cautomation_root).read_text(encoding="utf-8"))


def _error_codes(cautomation_root: Path) -> set[str]:
    return {error["code"] for error in _read_state(cautomation_root)["errors"]}


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(
        f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>"
        for paragraph in paragraphs
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body>"
        "</w:document>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)


def _valid_srs_text() -> str:
    return " ".join([
        "Purpose Scope Business Context Workflow Validation Acceptance",
        "This Pipeline Management SRS is part of CAutomation and CCore.",
        "The SRS references the ATS for architecture and implementation constraints.",
        "Detailed requirements " * 80,
    ])


def _valid_ats_text() -> str:
    return " ".join([
        "Architecture Traceability Database API Validation Testing",
        "This Pipeline Management ATS is part of CAutomation and CCore.",
        "The ATS references the SRS for functional intent and acceptance rules.",
        "Detailed technical design " * 80,
    ])


def _replace_reference_docs(cautomation_root: Path, srs_text: str | None = None, ats_text: str | None = None) -> None:
    if srs_text is not None:
        _write_minimal_docx(_module_root(cautomation_root) / "Software_Requirements_Specification.docx", [srs_text])
    if ats_text is not None:
        _write_minimal_docx(_module_root(cautomation_root) / "Architecture_and_Technical_Specification.docx", [ats_text])


def test_validate_inputs_accepts_structured_readable_non_empty_documents(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    _replace_reference_docs(cautomation_root, _valid_srs_text(), _valid_ats_text())

    result = _run_task(cautomation_root)

    assert result.returncode == 0
    state = _read_state(cautomation_root)
    assert state["status"] in {"PASSED", "PASSED_WITH_WARNINGS"}
    assert state["gateDecision"] == "ACCEPTED"
    assert not state["errors"]


def test_validate_inputs_rejects_missing_required_input_document(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    (_module_root(cautomation_root) / "Software_Requirements_Specification.docx").unlink()

    result = _run_task(cautomation_root)

    assert result.returncode == 1
    assert "module_srs_exists" in _error_codes(cautomation_root)


def test_validate_inputs_rejects_unreadable_docx_input(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    (_module_root(cautomation_root) / "Software_Requirements_Specification.docx").write_text("not a zip file", encoding="utf-8")

    result = _run_task(cautomation_root)

    assert result.returncode == 1
    assert "srs_unreadable_docx" in _error_codes(cautomation_root)


def test_validate_inputs_rejects_empty_extractable_document(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    _write_minimal_docx(_module_root(cautomation_root) / "Software_Requirements_Specification.docx", [])

    result = _run_task(cautomation_root)

    assert result.returncode == 1
    assert "srs_empty_document" in _error_codes(cautomation_root)


def test_validate_inputs_rejects_document_below_minimum_content_length(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    _replace_reference_docs(cautomation_root, "Purpose Scope Business Context Workflow Validation Acceptance CAutomation CCore Pipeline Management ATS")

    result = _run_task(cautomation_root)

    assert result.returncode == 1
    assert "srs_insufficient_content" in _error_codes(cautomation_root)


def test_validate_inputs_rejects_missing_required_template_section(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    missing_acceptance = _valid_srs_text().replace("Acceptance", "")
    _replace_reference_docs(cautomation_root, missing_acceptance, _valid_ats_text())

    result = _run_task(cautomation_root)

    assert result.returncode == 1
    assert "srs_missing_required_term" in _error_codes(cautomation_root)


def test_validate_inputs_rejects_unresolved_placeholder_tokens(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    _replace_reference_docs(cautomation_root, _valid_srs_text() + " TODO")

    result = _run_task(cautomation_root)

    assert result.returncode == 1
    assert "srs_placeholder_token_found" in _error_codes(cautomation_root)


def test_validate_inputs_rejects_missing_cross_document_reference(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    srs_without_ats = _valid_srs_text().replace("ATS", "architecture specification")
    _replace_reference_docs(cautomation_root, srs_without_ats, _valid_ats_text())

    result = _run_task(cautomation_root)

    assert result.returncode == 1
    assert "missing_cross_document_reference" in _error_codes(cautomation_root)


def test_validate_inputs_rejects_invalid_quality_gate_document_profile(tmp_path):
    cautomation_root = _copy_repo(tmp_path)
    config = _read_pipeline_config(cautomation_root)
    config["validation"]["inputQualityGate"]["manualInputDocuments"] = "not-an-array"
    _write_pipeline_config(cautomation_root, config)

    result = _run_task(cautomation_root)

    assert result.returncode == 1
    assert "invalid_input_quality_gate_config" in _error_codes(cautomation_root)
