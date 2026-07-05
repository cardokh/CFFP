"""Base contract for source document normalizers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NormalizationResult:
    """Canonical output from a source document normalizer."""

    markdown: str
    source_format: str


class DocumentNormalizer:
    """Base class for converting one source document format into Markdown."""

    source_format: str

    def normalize(self, path: Path) -> NormalizationResult:
        """Normalize a source document into canonical Markdown."""
        raise NotImplementedError
