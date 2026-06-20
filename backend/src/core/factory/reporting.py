"""Execution reporting for the CCore Automation Factory POC."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO format."""

    return datetime.now(timezone.utc).isoformat()


def write_execution_report(report_dir: Path, execution_id: str, report: dict[str, Any]) -> Path:
    """Write a JSON execution report."""

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{execution_id}.json"
    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2, sort_keys=True)
    return report_path
