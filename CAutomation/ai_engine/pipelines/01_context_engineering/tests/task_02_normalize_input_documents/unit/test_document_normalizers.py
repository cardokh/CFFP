from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path


def _cautomation_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir())


def _normalizer_root() -> Path:
    return _cautomation_root() / "ai_engine/pipelines/01_context_engineering/tasks/normalize_input_documents"


def _import_normalizers_package():
    root = _normalizer_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import document_normalizers  # noqa: PLC0415

    return document_normalizers


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>" for paragraph in paragraphs)
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body>"
        "</w:document>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)


def test_registry_supports_pdf_docx_and_markdown():
    document_normalizers = _import_normalizers_package()

    registry = document_normalizers.DocumentNormalizerRegistry()

    assert registry.supported_formats() == ["docx", "md", "pdf"]
    assert registry.supports("pdf")
    assert registry.supports("docx")
    assert registry.supports(".md")


def test_docx_normalizer_converts_docx_to_markdown(tmp_path):
    root = _normalizer_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from document_normalizers.docx_normalizer import DocxDocumentNormalizer  # noqa: PLC0415

    docx_path = tmp_path / "contract.docx"
    _write_minimal_docx(docx_path, ["Purpose", "Scope", "Acceptance"])

    result = DocxDocumentNormalizer().normalize(docx_path)

    assert result.source_format == "docx"
    assert "Purpose" in result.markdown
    assert "Scope" in result.markdown
    assert "Acceptance" in result.markdown


def test_markdown_normalizer_passes_markdown_through(tmp_path):
    root = _normalizer_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from document_normalizers.markdown_normalizer import MarkdownDocumentNormalizer  # noqa: PLC0415

    markdown_path = tmp_path / "contract.md"
    markdown_path.write_text("# Purpose\n\nContent", encoding="utf-8")

    result = MarkdownDocumentNormalizer().normalize(markdown_path)

    assert result.source_format == "md"
    assert result.markdown == "# Purpose\n\nContent\n"
