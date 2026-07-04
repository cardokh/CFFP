"""DOCX extraction utilities for CAutomation pipeline scripts.

The implementation intentionally uses only the Python standard library so the
first CAutomation pipeline can run from a clean checkout without external
packages.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class DocxReadError(RuntimeError):
    """Raised when a DOCX file cannot be read as a Word document."""


def _iter_text_nodes(element: ET.Element) -> Iterable[str]:
    for node in element.iter(f"{_WORD_NS}t"):
        if node.text:
            yield node.text


def _paragraph_text(paragraph: ET.Element) -> str:
    return "".join(_iter_text_nodes(paragraph)).strip()


def _table_as_markdown(table: ET.Element) -> str:
    rows: list[list[str]] = []
    for row in table.iter(f"{_WORD_NS}tr"):
        cells: list[str] = []
        for cell in row.iter(f"{_WORD_NS}tc"):
            paragraphs = [_paragraph_text(p) for p in cell.iter(f"{_WORD_NS}p")]
            value = " ".join(p for p in paragraphs if p).strip()
            cells.append(value.replace("|", "\\|"))
        if cells:
            rows.append(cells)

    if not rows:
        return ""

    max_cols = max(len(r) for r in rows)
    normalized = [r + [""] * (max_cols - len(r)) for r in rows]
    header = normalized[0]
    separator = ["---"] * max_cols
    body = normalized[1:]

    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(separator) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def read_docx_as_markdown(path: Path) -> str:
    """Extract a deterministic Markdown approximation of a DOCX file."""

    if not path.exists():
        raise DocxReadError(f"DOCX file does not exist: {path}")

    try:
        with ZipFile(path) as archive:
            xml_bytes = archive.read("word/document.xml")
    except (BadZipFile, KeyError) as exc:
        raise DocxReadError(f"Invalid or unsupported DOCX file: {path}") from exc

    root = ET.fromstring(xml_bytes)
    body = root.find(f"{_WORD_NS}body")
    if body is None:
        return ""

    blocks: list[str] = []
    for child in body:
        if child.tag == f"{_WORD_NS}p":
            text = _paragraph_text(child)
            if text:
                blocks.append(text)
        elif child.tag == f"{_WORD_NS}tbl":
            table = _table_as_markdown(child)
            if table:
                blocks.append(table)

    return "\n\n".join(blocks).strip() + "\n"
