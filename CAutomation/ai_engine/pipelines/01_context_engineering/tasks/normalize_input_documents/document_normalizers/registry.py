"""Registry for source document normalizers."""

from __future__ import annotations

from pathlib import Path

from .base import DocumentNormalizer, NormalizationResult
from .docx_normalizer import DocxDocumentNormalizer
from .markdown_normalizer import MarkdownDocumentNormalizer
from .pdf_normalizer import PdfDocumentNormalizer


class DocumentNormalizerRegistry:
    """Selects the correct normalizer for a source document path."""

    def __init__(self, normalizers: list[DocumentNormalizer] | None = None) -> None:
        configured_normalizers = normalizers or [
            PdfDocumentNormalizer(),
            DocxDocumentNormalizer(),
            MarkdownDocumentNormalizer(),
        ]
        self._normalizers = {normalizer.source_format: normalizer for normalizer in configured_normalizers}

    def supported_formats(self) -> list[str]:
        return sorted(self._normalizers)

    def supports(self, source_format: str) -> bool:
        return source_format.lower().lstrip(".") in self._normalizers

    def normalize(self, path: Path) -> NormalizationResult:
        source_format = path.suffix.lower().lstrip(".")
        normalizer = self._normalizers.get(source_format)
        if normalizer is None:
            raise RuntimeError(f"Unsupported source document format: {path.suffix or '<none>'}")
        return normalizer.normalize(path)
