"""Factory task execution report writing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .validation import ensure_child_path


@dataclass(frozen=True)
class FactoryTaskReportRecord:
    """Metadata for one persisted Factory execution report."""

    path: str
    size_bytes: int

    def to_dict(self) -> dict[str, object]:
        """Return a serializable report record."""

        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class FactoryTaskReportWriter:
    """Writes Factory execution reports outside the source tree."""

    report_root: Path

    def write_report(
        self,
        *,
        execution_id: str,
        task_id: str,
        report: dict[str, Any],
    ) -> FactoryTaskReportRecord:
        """Write one execution report and return metadata."""

        safe_task_id = _safe_path_segment(task_id)
        report_dir = self.report_root / safe_task_id
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"{execution_id}.json"
        ensure_child_path(self.report_root, report_path)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return FactoryTaskReportRecord(
            path=str(report_path),
            size_bytes=report_path.stat().st_size,
        )


def _safe_path_segment(value: str) -> str:
    cleaned = "".join(character if character.isalnum() or character in ("-", "_") else "-" for character in value)
    return cleaned.strip("-") or "factory-task"
