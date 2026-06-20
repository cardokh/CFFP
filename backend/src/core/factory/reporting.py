"""Execution report writing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""

    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class JsonReportWriter:
    """Writes Factory execution reports as JSON."""

    def write_report(
        self,
        report_dir: Path,
        execution_id: str,
        report: dict[str, Any],
    ) -> Path:
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"{execution_id}.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return report_path


def write_execution_report(
    report_dir: Path,
    execution_id: str,
    report: dict[str, Any],
) -> Path:
    """Backward-compatible report writer function."""

    return JsonReportWriter().write_report(report_dir, execution_id, report)
