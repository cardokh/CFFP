from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _cautomation_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir())


def _load_task_class():
    cautomation_root = _cautomation_root()
    for import_root in (cautomation_root, cautomation_root.parent):
        if str(import_root) not in sys.path:
            sys.path.insert(0, str(import_root))
    module_path = cautomation_root / "ai_engine/pipelines/01_context_engineering/tasks/normalize_input_documents/normalize_input_documents.py"
    spec = importlib.util.spec_from_file_location("normalize_input_documents_task", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.NormalizeInputDocumentsTask


def test_normalize_input_documents_loads_pipeline_config(monkeypatch):
    cautomation_root = _cautomation_root()
    monkeypatch.chdir(cautomation_root.parent)

    task = _load_task_class()()

    assert task.pipeline_config["pipelineId"] == "01_context_engineering"
    assert task.pipeline_config["validation"]["inputQualityGate"]["enabled"] is True


def test_normalize_input_documents_resolves_required_contract_paths(monkeypatch):
    cautomation_root = _cautomation_root()
    monkeypatch.chdir(cautomation_root.parent)

    task = _load_task_class()()
    srs_path, ats_path = task.contract_paths()

    assert srs_path.name == "Software_Requirements_Specification.pdf"
    assert ats_path.name == "Architecture_and_Technical_Specification.pdf"
    assert "projects/pipeline_management/input/modules/pipeline_management" in task.to_project_relative_path(srs_path)


def test_normalize_input_documents_term_matching_is_case_insensitive(monkeypatch):
    cautomation_root = _cautomation_root()
    monkeypatch.chdir(cautomation_root.parent)

    task = _load_task_class()()

    assert task._contains_term("This document defines acceptance criteria.", "Acceptance")
    assert task._contains_term("The ats references the srs.", "ATS")
    assert not task._contains_term("No matching phrase here.", "Acceptance")


def test_normalize_input_documents_safe_check_names_are_stable(monkeypatch):
    cautomation_root = _cautomation_root()
    monkeypatch.chdir(cautomation_root.parent)

    task = _load_task_class()()

    assert task._safe_check_name("Pipeline Management") == "pipeline_management"
    assert task._safe_check_name("???") == "value"


def test_normalize_input_documents_uses_document_normalizer_registry(monkeypatch):
    cautomation_root = _cautomation_root()
    monkeypatch.chdir(cautomation_root.parent)

    task = _load_task_class()()

    assert task.document_normalizers.supports("docx")
    assert task.document_normalizers.supports("pdf")
    assert task.document_normalizers.supports("md")


def test_normalize_input_documents_supported_formats_are_configured_and_registered(monkeypatch):
    cautomation_root = _cautomation_root()
    monkeypatch.chdir(cautomation_root.parent)

    task = _load_task_class()()
    quality_gate = task.pipeline_config["validation"]["inputQualityGate"]
    configured_formats = set(quality_gate["supportedSourceFormats"])

    assert "pdf" in configured_formats
    assert all(task.document_normalizers.supports(source_format) for source_format in configured_formats)
