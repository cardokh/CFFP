from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.factory_run_models import FactoryRun  # noqa: E402
from scripts.shared.script_json_utils import write_json_file  # noqa: E402
from scripts.shared.script_path_utils import get_project_root, to_relative_path  # noqa: E402


class FactoryRunReportWriter:
    """Writes one high-level report for a local Automation Factory run."""

    REPORT_FILE_NAME = "factory_run_report.json"
    COMPILATION_REPORT_FILE_NAME = "master-context-compilation-report.json"
    GENERATION_REPORT_FILE_NAME = "generation_report.json"
    VALIDATION_REPORT_FILE_NAME = "validation_apply_report.json"

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or get_project_root()

    def write_report(self, factory_run: FactoryRun) -> Path:
        execution_root = self.execution_root(factory_run.execution_id)
        report_path = execution_root / self.REPORT_FILE_NAME
        report = self.build_report(factory_run)
        write_json_file(report_path, report)
        return report_path

    def build_report(self, factory_run: FactoryRun) -> dict[str, Any]:
        execution_root = self.execution_root(factory_run.execution_id)
        stage_reports = {
            "contextCompiler": self._read_optional_json(execution_root / self.COMPILATION_REPORT_FILE_NAME),
            "aiGenerationEngine": self._read_optional_json(execution_root / self.GENERATION_REPORT_FILE_NAME),
            "validationApplyEngine": self._read_optional_json(execution_root / self.VALIDATION_REPORT_FILE_NAME),
        }
        return {
            "reportType": "factory-run-orchestrator",
            "reportVersion": "4.0",
            "status": factory_run.status.value,
            "executionId": factory_run.execution_id,
            "workspace": {
                "executionRoot": to_relative_path(self.project_root, execution_root),
                "reportPath": to_relative_path(self.project_root, execution_root / self.REPORT_FILE_NAME),
            },
            "timestamps": {
                "startedAt": factory_run.started_at,
                "finishedAt": factory_run.finished_at,
            },
            "stages": [stage.to_dict() for stage in factory_run.stages],
            "stageReports": stage_reports,
        }

    def execution_root(self, execution_id: str) -> Path:
        return self.project_root / ".ccore_workspace" / "staging" / execution_id

    def _read_optional_json(self, file_path: Path) -> dict[str, Any] | None:
        if not file_path.exists() or not file_path.is_file():
            return None
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {
                "status": "FAILED",
                "error": {
                    "code": "INVALID_JSON_REPORT",
                    "message": str(exc),
                    "path": to_relative_path(self.project_root, file_path),
                },
            }
