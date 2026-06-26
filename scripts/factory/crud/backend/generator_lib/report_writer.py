"""Report writing helpers for backend CRUD automation."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_report(repo_root: Path, report_path: str | None, report: dict[str, Any]) -> None:
    if not report_path:
        return
    target_path = repo_root / report_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(report, indent=4), encoding="utf-8", newline="\n")
