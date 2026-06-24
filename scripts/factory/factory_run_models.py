from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class FactoryRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class FactoryStageStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"


@dataclass
class FactoryStage:
    name: str
    status: FactoryStageStatus = FactoryStageStatus.PENDING
    started_at: str | None = None
    finished_at: str | None = None
    report_path: str | None = None
    error_message: str | None = None

    def mark_running(self) -> None:
        self.status = FactoryStageStatus.RUNNING
        self.started_at = utc_now()
        self.finished_at = None
        self.error_message = None

    def mark_passed(self, report_path: str | None = None) -> None:
        self.status = FactoryStageStatus.PASSED
        self.finished_at = utc_now()
        self.report_path = report_path

    def mark_failed(self, error_message: str, report_path: str | None = None) -> None:
        self.status = FactoryStageStatus.FAILED
        self.finished_at = utc_now()
        self.error_message = error_message
        self.report_path = report_path

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "startedAt": self.started_at,
            "finishedAt": self.finished_at,
            "reportPath": self.report_path,
            "errorMessage": self.error_message,
        }


@dataclass
class FactoryRun:
    execution_id: str
    status: FactoryRunStatus = FactoryRunStatus.PENDING
    started_at: str | None = None
    finished_at: str | None = None
    stages: list[FactoryStage] = field(default_factory=list)
    report_path: str | None = None

    def mark_running(self) -> None:
        self.status = FactoryRunStatus.RUNNING
        self.started_at = utc_now()
        self.finished_at = None

    def mark_passed(self, report_path: str | None = None) -> None:
        self.status = FactoryRunStatus.PASSED
        self.finished_at = utc_now()
        self.report_path = report_path

    def mark_failed(self, report_path: str | None = None) -> None:
        self.status = FactoryRunStatus.FAILED
        self.finished_at = utc_now()
        self.report_path = report_path

    def to_dict(self) -> dict[str, Any]:
        return {
            "executionId": self.execution_id,
            "status": self.status.value,
            "startedAt": self.started_at,
            "finishedAt": self.finished_at,
            "reportPath": self.report_path,
            "stages": [stage.to_dict() for stage in self.stages],
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
