"""Markdown document normalizer."""

from __future__ import annotations

from pathlib import Path

from .base import DocumentNormalizer, NormalizationResult


class MarkdownDocumentNormalizer(DocumentNormalizer):
    """Passes Markdown source documents through as canonical Markdown."""

    source_format = "md"

    def normalize(self, path: Path) -> NormalizationResult:
        text = path.read_text(encoding="utf-8").strip()
        return NormalizationResult(markdown=(text + "\n") if text else "", source_format=self.source_format)
