from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.factory_run_orchestrator import FactoryRunOrchestrator  # noqa: E402


class ValidationFailure(AssertionError):
    pass


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def remove_execution_root(execution_id: str) -> None:
    execution_root = PROJECT_ROOT / ".ccore_workspace" / "staging" / execution_id
    if execution_root.exists():
        shutil.rmtree(execution_root)


def validate_successful_orchestration() -> tuple[str, dict[str, Any]]:
    execution_id = f"iter4-validation-{uuid.uuid4().hex[:12]}"
    remove_execution_root(execution_id)

    factory_run = FactoryRunOrchestrator(PROJECT_ROOT).run(execution_id=execution_id)
    execution_root = PROJECT_ROOT / ".ccore_workspace" / "staging" / execution_id
    report_path = execution_root / "factory_run_report.json"

    assert_true(factory_run.status.value == "PASSED", "Factory run should pass.")
    assert_true(report_path.exists(), "factory_run_report.json should exist.")

    report = read_json(report_path)
    assert_true(report["executionId"] == execution_id, "Factory report should use requested executionId.")
    assert_true(report["status"] == "PASSED", "Factory report status should be PASSED.")

    expected_stage_names = ["contextCompiler", "aiGenerationEngine", "validationApplyEngine"]
    actual_stage_names = [stage["name"] for stage in report["stages"]]
    assert_true(actual_stage_names == expected_stage_names, "Stages should be ordered compiler -> generator -> validator.")
    assert_true(all(stage["status"] == "PASSED" for stage in report["stages"]), "All stages should pass.")

    for file_name in [
        "master-context.md",
        "master-context-compilation-report.json",
        "prompt.txt",
        "raw_response.txt",
        "artifact_manifest.json",
        "generation_report.json",
        "validation_apply_report.json",
        "factory_run_report.json",
    ]:
        assert_true((execution_root / file_name).exists(), f"Expected output missing: {file_name}")

    assert_true(
        report["stageReports"]["contextCompiler"]["summary"]["status"] == "PASSED",
        "Compiler stage report should be aggregated.",
    )
    assert_true(
        report["stageReports"]["aiGenerationEngine"]["executionId"] == execution_id,
        "Generation report should use orchestrator executionId.",
    )
    assert_true(
        report["stageReports"]["validationApplyEngine"]["status"] == "PASSED",
        "Validation/apply stage report should be aggregated.",
    )

    return execution_id, report


def validate_failed_existing_execution_id() -> None:
    execution_id = f"iter4-existing-{uuid.uuid4().hex[:12]}"
    execution_root = PROJECT_ROOT / ".ccore_workspace" / "staging" / execution_id
    remove_execution_root(execution_id)
    execution_root.mkdir(parents=True)

    try:
        FactoryRunOrchestrator(PROJECT_ROOT).run(execution_id=execution_id)
    except FileExistsError:
        return
    finally:
        remove_execution_root(execution_id)

    raise ValidationFailure("Existing execution root should be rejected before stage execution.")


def validate_no_forbidden_web_artifacts() -> None:
    forbidden_paths = [
        PROJECT_ROOT / "scripts" / "factory" / "endpoints",
        PROJECT_ROOT / "scripts" / "factory" / "factory_run_endpoint.py",
    ]
    for path in forbidden_paths:
        assert_true(not path.exists(), f"Forbidden web/API artifact exists: {path}")


def validate_compile_and_independent_engines() -> None:
    files_to_compile = [
        "scripts/factory/factory_run_models.py",
        "scripts/factory/factory_run_report_writer.py",
        "scripts/factory/factory_run_orchestrator.py",
        "scripts/factory/context_compiler/master_context_compiler.py",
        "scripts/factory/ai_generation_engine/ai_generation_engine.py",
        "scripts/factory/validation_apply_engine/validation_apply_engine.py",
    ]
    subprocess.run(
        [sys.executable, "-m", "py_compile", *files_to_compile],
        cwd=PROJECT_ROOT,
        check=True,
    )

    for engine_file in [
        PROJECT_ROOT / "scripts" / "factory" / "context_compiler" / "master_context_compiler.py",
        PROJECT_ROOT / "scripts" / "factory" / "ai_generation_engine" / "ai_generation_engine.py",
        PROJECT_ROOT / "scripts" / "factory" / "validation_apply_engine" / "validation_apply_engine.py",
    ]:
        assert_true(engine_file.exists(), f"Independent engine file missing: {engine_file}")


def main() -> None:
    checks = [
        ("successful orchestrator run", lambda: validate_successful_orchestration()),
        ("single executionId across reports", lambda: validate_successful_orchestration()),
        ("existing execution root rejected", validate_failed_existing_execution_id),
        ("no endpoint/API artifacts", validate_no_forbidden_web_artifacts),
        ("compile validation and independent engines", validate_compile_and_independent_engines),
    ]

    passed = 0
    for check_name, check in checks:
        check()
        passed += 1
        print(f"PASS {check_name}")

    print(f"PASS validate_factory_run_orchestrator: {passed}/{len(checks)} checks passed")


if __name__ == "__main__":
    main()
