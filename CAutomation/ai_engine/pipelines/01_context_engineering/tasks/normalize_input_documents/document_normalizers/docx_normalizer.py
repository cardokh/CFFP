"""DOCX document normalizer."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from .base import DocumentNormalizer, NormalizationResult


_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class DocxDocumentNormalizer(DocumentNormalizer):
    """Converts DOCX documents into canonical Markdown text."""

    source_format = "docx"

    def normalize(self, path: Path) -> NormalizationResult:
        try:
            with ZipFile(path) as archive:
                xml_bytes = archive.read("word/document.xml")
        except (BadZipFile, KeyError) as exc:
            raise RuntimeError(f"Invalid or unsupported DOCX file: {path}") from exc

        root = ET.fromstring(xml_bytes)
        body = root.find(f"{_WORD_NS}body")
        if body is None:
            return NormalizationResult(markdown="", source_format=self.source_format)

        blocks: list[str] = []
        for child in body:
            if child.tag == f"{_WORD_NS}p":
                text = self._paragraph_text(child)
                if text:
                    blocks.append(text)
            elif child.tag == f"{_WORD_NS}tbl":
                table = self._table_as_markdown(child)
                if table:
                    blocks.append(table)
        markdown = "\n\n".join(blocks).strip()
        return NormalizationResult(markdown=(markdown + "\n") if markdown else "", source_format=self.source_format)

    def _paragraph_text(self, paragraph: ET.Element) -> str:
        return "".join(self._iter_text_nodes(paragraph)).strip()

    def _iter_text_nodes(self, element: ET.Element) -> Iterable[str]:
        for node in element.iter(f"{_WORD_NS}t"):
            if node.text:
                yield node.text

    def _table_as_markdown(self, table: ET.Element) -> str:
        rows: list[list[str]] = []
        for row in table.iter(f"{_WORD_NS}tr"):
            cells: list[str] = []
            for cell in row.iter(f"{_WORD_NS}tc"):
                paragraphs = [self._paragraph_text(p) for p in cell.iter(f"{_WORD_NS}p")]
                value = " ".join(p for p in paragraphs if p).strip()
                cells.append(value.replace("|", "\|"))
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        max_cols = max(len(row) for row in rows)
        normalized = [row + [""] * (max_cols - len(row)) for row in rows]
        header = normalized[0]
        separator = ["---"] * max_cols
        body = normalized[1:]
        lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(separator) + " |"]
        lines.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(lines)
