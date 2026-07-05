"""PDF document normalizer."""

from __future__ import annotations

from pathlib import Path

from .base import DocumentNormalizer, NormalizationResult


class PdfDocumentNormalizer(DocumentNormalizer):
    """Converts text-based PDF documents into canonical Markdown text."""

    source_format = "pdf"

    def normalize(self, path: Path) -> NormalizationResult:
        try:
            from pypdf import PdfReader  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("PDF normalization requires the optional pypdf dependency.") from exc

        reader = PdfReader(str(path))
        pages: list[str] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append(f"<!-- page: {index} -->\n\n{text}")
        markdown = "\n\n".join(pages).strip()
        return NormalizationResult(markdown=(markdown + "\n") if markdown else "", source_format=self.source_format)
