"""Shared helpers for Pipeline 01 - Context Engineering tasks."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


_PROJECT_ROOT = next(
    (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
    None,
)
if _PROJECT_ROOT is not None and str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from CAutomation.ai_engine.runtime.task_runtime import (  # noqa: E402
    RuntimeTaskSupportMixin,
    clean_directory,
    configure_project_import_path,
    source_record,
    utc_now_iso,
)


_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class ContextEngineeringSupportMixin(RuntimeTaskSupportMixin):
    """Pipeline 01 specific runtime support."""

    def contract_paths(self) -> tuple[Path, Path]:
        input_config = self.group("input")
        module_root = self.module_input_root()
        return module_root / input_config["srsFileName"], module_root / input_config["atsFileName"]

    def context_package_dir(self) -> Path:
        output_config = self.group("output")
        package_root = self.CAutomation_root() / self.resolve_placeholders(output_config["contextPackageRoot"])
        package_id = self.resolve_placeholders(output_config["contextPackageId"])
        return (package_root / package_id).resolve()


def read_docx_as_markdown(path: Path) -> str:
    try:
        with ZipFile(path) as archive:
            xml_bytes = archive.read("word/document.xml")
    except (BadZipFile, KeyError) as exc:
        raise RuntimeError(f"Invalid or unsupported DOCX file: {path}") from exc

    root = ET.fromstring(xml_bytes)
    body = root.find(f"{_WORD_NS}body")
    if body is None:
        return ""

    blocks: list[str] = []
    for child in body:
        if child.tag == f"{_WORD_NS}p":
            text = paragraph_text(child)
            if text:
                blocks.append(text)
        elif child.tag == f"{_WORD_NS}tbl":
            table = table_as_markdown(child)
            if table:
                blocks.append(table)
    return "\n\n".join(blocks).strip() + "\n"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(iter_text_nodes(paragraph)).strip()


def iter_text_nodes(element: ET.Element) -> Iterable[str]:
    for node in element.iter(f"{_WORD_NS}t"):
        if node.text:
            yield node.text


def table_as_markdown(table: ET.Element) -> str:
    rows: list[list[str]] = []
    for row in table.iter(f"{_WORD_NS}tr"):
        cells: list[str] = []
        for cell in row.iter(f"{_WORD_NS}tc"):
            paragraphs = [paragraph_text(p) for p in cell.iter(f"{_WORD_NS}p")]
            value = " ".join(p for p in paragraphs if p).strip()
            cells.append(value.replace("|", "\\|"))
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
