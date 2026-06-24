from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.ai_generation_engine.ai_generation_engine import AiGenerationEngine  # noqa: E402
from scripts.factory.context_compiler.master_context_compiler import MasterContextCompiler  # noqa: E402
from scripts.factory.factory_run_models import FactoryRun, FactoryRunStatus, FactoryStage  # noqa: E402
from scripts.factory.factory_run_report_writer import FactoryRunReportWriter  # noqa: E402
from scripts.factory.validation_apply_engine.validation_apply_engine import ValidationApplyEngine  # noqa: E402
from scripts.shared.script_json_utils import read_json_file  # noqa: E402
from scripts.shared.script_path_utils import get_project_root, to_relative_path  # noqa: E402


class FactoryRunOrchestrator:
    """Local CLI orchestration layer for Automation Factory Iterations 1, 2, and 3."""

    STAGE_CONTEXT_COMPILER = "contextCompiler"
    STAGE_AI_GENERATION_ENGINE = "aiGenerationEngine"
    STAGE_VALIDATION_APPLY_ENGINE = "validationApplyEngine"

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or get_project_root()
        self.report_writer = FactoryRunReportWriter(self.project_root)

    def run(self, execution_id: str | None = None, apply_mode: str = "validate-only") -> FactoryRun:
        normalized_execution_id = self._normalize_execution_id(execution_id or self._new_execution_id())
        factory_run = FactoryRun(
            execution_id=normalized_execution_id,
            stages=[
                FactoryStage(self.STAGE_CONTEXT_COMPILER),
                FactoryStage(self.STAGE_AI_GENERATION_ENGINE),
                FactoryStage(self.STAGE_VALIDATION_APPLY_ENGINE),
            ],
        )
        factory_run.mark_running()

        self._ensure_execution_root(normalized_execution_id)

        try:
            self._run_stage(
                factory_run,
                self.STAGE_CONTEXT_COMPILER,
                lambda: self._run_context_compiler(normalized_execution_id),
                "master-context-compilation-report.json",
            )
            self._run_stage(
                factory_run,
                self.STAGE_AI_GENERATION_ENGINE,
                lambda: self._run_ai_generation_engine(normalized_execution_id),
                "generation_report.json",
            )
            self._run_stage(
                factory_run,
                self.STAGE_VALIDATION_APPLY_ENGINE,
                lambda: self._run_validation_apply_engine(normalized_execution_id, apply_mode),
                "validation_apply_report.json",
            )
            factory_run.mark_passed()
        except Exception:  # noqa: BLE001 - stage already records explicit failure metadata.
            factory_run.mark_failed()

        report_path = self.report_writer.write_report(factory_run)
        factory_run.report_path = to_relative_path(self.project_root, report_path)
        self.report_writer.write_report(factory_run)
        return factory_run

    def _run_stage(
        self,
        factory_run: FactoryRun,
        stage_name: str,
        stage_callable: Callable[[], None],
        report_file_name: str,
    ) -> None:
        stage = self._stage(factory_run, stage_name)
        stage.mark_running()
        report_path = self._execution_root(factory_run.execution_id) / report_file_name
        try:
            stage_callable()
            self._assert_report_passed(report_path)
            stage.mark_passed(to_relative_path(self.project_root, report_path))
        except Exception as exc:  # noqa: BLE001 - fail-fast pipeline boundary.
            stage.mark_failed(str(exc), to_relative_path(self.project_root, report_path) if report_path.exists() else None)
            raise

    def _run_context_compiler(self, execution_id: str) -> None:
        engine = MasterContextCompiler()
        execution_root = self._execution_root(execution_id)
        engine.config.setdefault("outputs", {})["masterContextPath"] = to_relative_path(
            self.project_root,
            execution_root / "master-context.md",
        )
        engine.config.setdefault("outputs", {})["reportPath"] = to_relative_path(
            self.project_root,
            execution_root / "master-context-compilation-report.json",
        )
        engine.run()

    def _run_ai_generation_engine(self, execution_id: str) -> None:
        engine = AiGenerationEngine()
        execution_root = self._execution_root(execution_id)
        engine.config.setdefault("inputs", {})["masterContextPath"] = to_relative_path(
            self.project_root,
            execution_root / "master-context.md",
        )
        engine.config.setdefault("inputs", {})["executionId"] = execution_id
        engine.config.setdefault("outputs", {})["stagingRoot"] = ".ccore_workspace/staging/{executionId}"
        engine.run()

    def _run_validation_apply_engine(self, execution_id: str, apply_mode: str) -> None:
        engine = ValidationApplyEngine()
        engine.config.setdefault("inputs", {})["executionId"] = execution_id
        engine.config.setdefault("inputs", {})["stagingRoot"] = ".ccore_workspace/staging"
        engine.config.setdefault("apply", {})["mode"] = apply_mode
        engine.run()

    def _assert_report_passed(self, report_path: Path) -> None:
        if not report_path.exists() or not report_path.is_file():
            raise FileNotFoundError(f"Expected stage report was not created: {report_path}")
        report = read_json_file(report_path)
        status = report.get("status") or report.get("summary", {}).get("status")
        if status != "PASSED":
            raise RuntimeError(f"Stage report status is not PASSED: {report_path} status={status}")

    def _stage(self, factory_run: FactoryRun, stage_name: str) -> FactoryStage:
        for stage in factory_run.stages:
            if stage.name == stage_name:
                return stage
        raise ValueError(f"Unknown factory run stage: {stage_name}")

    def _ensure_execution_root(self, execution_id: str) -> Path:
        execution_root = self._execution_root(execution_id)
        execution_root.mkdir(parents=True, exist_ok=False)
        return execution_root

    def _execution_root(self, execution_id: str) -> Path:
        return self.project_root / ".ccore_workspace" / "staging" / execution_id

    def _new_execution_id(self) -> str:
        return f"factory-run-{uuid.uuid4().hex[:16]}"

    def _normalize_execution_id(self, execution_id: str) -> str:
        value = execution_id.strip()
        if not value:
            raise ValueError("execution_id must not be blank.")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
            raise ValueError("execution_id may contain only letters, numbers, dots, underscores, and hyphens.")
        if ".." in value or "/" in value or "\\" in value:
            raise ValueError("execution_id must not contain path traversal or path separators.")
        return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local CFFP Automation Factory pipeline.")
    parser.add_argument("--execution-id", dest="execution_id", default=None)
    parser.add_argument(
        "--mode",
        dest="apply_mode",
        default="validate-only",
        choices=["validate-only", "validate-and-apply"],
    )
    args = parser.parse_args()

    factory_run = FactoryRunOrchestrator().run(
        execution_id=args.execution_id,
        apply_mode=args.apply_mode,
    )
    print(
        f"{factory_run.status.value} factory_run_orchestrator: "
        f"executionId={factory_run.execution_id}, report={factory_run.report_path}"
    )
    if factory_run.status == FactoryRunStatus.FAILED:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
