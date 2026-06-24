from __future__ import annotations

import copy
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.validation_apply_engine.validation_apply_contracts import (  # noqa: E402
    StagedArtifact,
    ValidationContext,
)
from scripts.factory.validation_apply_engine.validation_apply_engine import (  # noqa: E402
    ValidationApplyEngine,
)
from scripts.factory.validation_apply_engine.validation_apply_validators import (  # noqa: E402
    DirectoryTargetProtectionValidator,
)
from scripts.shared.script_json_utils import read_json_file, write_json_file  # noqa: E402


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    details: str


TEST_PREFIX = "af31_af32_validation"
STAGING_ROOT = PROJECT_ROOT / ".ccore_workspace" / "staging"
LIVE_SANDBOX_ROOT = PROJECT_ROOT / "backend" / "src" / "cffp_af31_af32_validation_sandbox"
ENGINE_CONFIG_PATH = PROJECT_ROOT / "scripts" / "factory" / "validation_apply_engine" / "config" / "validation_apply_engine.json"


def main() -> None:
    cleanup()
    base_config = read_json_file(ENGINE_CONFIG_PATH)
    results: list[CheckResult] = []

    try:
        valid_execution_id = f"{TEST_PREFIX}_valid"
        create_execution(
            execution_id=valid_execution_id,
            artifacts=[
                {
                    "artifactType": "python-source",
                    "targetPath": "backend/src/cffp_af31_af32_validation_sandbox/valid_pass.py",
                    "content": "VALUE = 1\n",
                    "reason": "AF-31 valid executionId verification artifact.",
                }
            ],
        )

        results.append(check_missing_execution_id_fails(base_config))
        results.append(check_invalid_execution_id_fails(base_config))
        results.append(check_valid_execution_id_passes(base_config, valid_execution_id))
        results.append(check_existing_directory_target_fails(base_config))
        results.append(check_parent_path_file_fails(base_config))
        results.append(check_directory_file_collision_fails(base_config))
    finally:
        cleanup()

    print_report(results)
    if any(not result.passed for result in results):
        raise SystemExit(1)


def check_missing_execution_id_fails(base_config: dict[str, Any]) -> CheckResult:
    def action() -> None:
        config = configured(base_config, execution_id=None)
        run_engine(config)

    passed, details = expect_exception_contains(
        action,
        expected_text="EXECUTION_ID_REQUIRED",
    )
    return CheckResult(
        name="AF-31 missing executionId fails fast",
        passed=passed,
        details=details,
    )


def check_invalid_execution_id_fails(base_config: dict[str, Any]) -> CheckResult:
    def action() -> None:
        config = configured(base_config, execution_id=f"{TEST_PREFIX}_does_not_exist")
        run_engine(config)

    passed, details = expect_exception_contains(
        action,
        expected_text="EXECUTION_NOT_FOUND",
    )
    return CheckResult(
        name="AF-31 invalid executionId fails fast",
        passed=passed,
        details=details,
    )


def check_valid_execution_id_passes(base_config: dict[str, Any], execution_id: str) -> CheckResult:
    config = configured(base_config, execution_id=execution_id)
    try:
        run_engine(config)
        report = read_report(execution_id)
    except Exception as exc:  # noqa: BLE001 - test harness reports full failure.
        return CheckResult(
            name="AF-31 valid executionId validates selected execution",
            passed=False,
            details=f"Unexpected exception: {exc}",
        )

    status = report.get("validation", {}).get("status")
    if status == "PASSED":
        return CheckResult(
            name="AF-31 valid executionId validates selected execution",
            passed=True,
            details="Validation status PASSED.",
        )

    return CheckResult(
        name="AF-31 valid executionId validates selected execution",
        passed=False,
        details=f"Expected validation PASSED, got {status}. Codes: {issue_codes(report)}",
    )


def check_existing_directory_target_fails(base_config: dict[str, Any]) -> CheckResult:
    execution_id = f"{TEST_PREFIX}_directory_target"
    target_relative = "backend/src/cffp_af31_af32_validation_sandbox/existing_directory_target"
    (PROJECT_ROOT / target_relative).mkdir(parents=True, exist_ok=True)

    create_execution(
        execution_id=execution_id,
        artifacts=[
            {
                "artifactType": "python-source",
                "targetPath": target_relative,
                "content": "VALUE = 2\n",
                "reason": "AF-32 existing directory target verification artifact.",
            }
        ],
    )

    return check_report_contains_code(
        base_config=base_config,
        execution_id=execution_id,
        check_name="AF-32 existing directory target is rejected",
        expected_code="TARGET_IS_DIRECTORY",
    )


def check_parent_path_file_fails(base_config: dict[str, Any]) -> CheckResult:
    execution_id = f"{TEST_PREFIX}_parent_file"
    parent_relative = "backend/src/cffp_af31_af32_validation_sandbox/parent_path_is_file"
    target_relative = f"{parent_relative}/child.py"
    parent_path = PROJECT_ROOT / parent_relative
    parent_path.parent.mkdir(parents=True, exist_ok=True)
    parent_path.write_text("not a directory\n", encoding="utf-8")

    create_execution(
        execution_id=execution_id,
        artifacts=[
            {
                "artifactType": "python-source",
                "targetPath": target_relative,
                "content": "VALUE = 3\n",
                "reason": "AF-32 parent path file verification artifact.",
            }
        ],
    )

    return check_report_contains_code(
        base_config=base_config,
        execution_id=execution_id,
        check_name="AF-32 parent path file is rejected",
        expected_code="PARENT_PATH_NOT_DIRECTORY",
    )


def check_directory_file_collision_fails(base_config: dict[str, Any]) -> CheckResult:
    execution_id = f"{TEST_PREFIX}_directory_file_collision"
    execution_root = STAGING_ROOT / execution_id
    artifacts_root = execution_root / "artifacts"
    artifacts_root.mkdir(parents=True, exist_ok=True)
    staged_a = artifacts_root / "artifact_a.py"
    staged_b = artifacts_root / "artifact_b.py"
    staged_a.write_text("VALUE = 4\n", encoding="utf-8")
    staged_b.write_text("VALUE = 5\n", encoding="utf-8")

    config = configured(base_config, execution_id=execution_id)
    context = ValidationContext(
        project_root=PROJECT_ROOT,
        execution_root=execution_root,
        artifacts_root=artifacts_root,
        manifest_path=execution_root / "artifact_manifest.json",
        artifacts=[
            StagedArtifact(
                artifact_type="python-source",
                target_path="backend/src/cffp_af31_af32_validation_sandbox/collision_target",
                staged_path=staged_a,
                content_sha256="not-needed-for-this-validator",
                size_bytes=staged_a.stat().st_size,
                line_count=1,
                reason="AF-32 directory/file collision base artifact.",
            ),
            StagedArtifact(
                artifact_type="python-source",
                target_path="backend/src/cffp_af31_af32_validation_sandbox/collision_target/child.py",
                staged_path=staged_b,
                content_sha256="not-needed-for-this-validator",
                size_bytes=staged_b.stat().st_size,
                line_count=1,
                reason="AF-32 directory/file collision child artifact.",
            ),
        ],
        config=config,
    )

    try:
        result = DirectoryTargetProtectionValidator().validate(context)
    except Exception as exc:  # noqa: BLE001 - absence/import mismatch should fail clearly.
        return CheckResult(
            name="AF-32 manifest directory/file collision is rejected",
            passed=False,
            details=f"Unexpected exception: {exc}",
        )

    codes = [issue.code for issue in result.issues]
    if "DIRECTORY_FILE_COLLISION" in codes:
        return CheckResult(
            name="AF-32 manifest directory/file collision is rejected",
            passed=True,
            details="Found DIRECTORY_FILE_COLLISION.",
        )

    return CheckResult(
        name="AF-32 manifest directory/file collision is rejected",
        passed=False,
        details=f"Expected DIRECTORY_FILE_COLLISION, got {codes}",
    )


def check_report_contains_code(
    *,
    base_config: dict[str, Any],
    execution_id: str,
    check_name: str,
    expected_code: str,
) -> CheckResult:
    config = configured(base_config, execution_id=execution_id)
    try:
        run_engine(config)
        report = read_report(execution_id)
    except Exception as exc:  # noqa: BLE001 - validation should report, not crash.
        return CheckResult(
            name=check_name,
            passed=False,
            details=f"Unexpected exception: {exc}",
        )

    codes = issue_codes(report)
    if expected_code in codes:
        return CheckResult(
            name=check_name,
            passed=True,
            details=f"Found {expected_code}.",
        )

    return CheckResult(
        name=check_name,
        passed=False,
        details=f"Expected {expected_code}, got {codes}",
    )


def run_engine(config: dict[str, Any]) -> None:
    engine = ValidationApplyEngine()
    engine.config = config
    engine.run()


def configured(base_config: dict[str, Any], execution_id: str | None) -> dict[str, Any]:
    config = copy.deepcopy(base_config)
    config.setdefault("inputs", {})["stagingRoot"] = ".ccore_workspace/staging"
    config.setdefault("inputs", {})["executionId"] = execution_id
    config.setdefault("outputs", {})["reportFileName"] = "validation_apply_report.json"
    config.setdefault("apply", {})["mode"] = "validate-only"
    config.setdefault("apply", {})["overwritePolicy"] = "FAIL"
    config.setdefault("validation", {})["pythonCompileEnabled"] = True
    config.setdefault("validation", {})["styleValidationEnabled"] = True
    return config


def create_execution(execution_id: str, artifacts: list[dict[str, str]]) -> None:
    execution_root = STAGING_ROOT / execution_id
    artifacts_root = execution_root / "artifacts"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    manifest_artifacts = []
    for artifact in artifacts:
        target_path = artifact["targetPath"].replace("\\", "/").strip("/")
        staged_path = artifacts_root / target_path
        staged_path.parent.mkdir(parents=True, exist_ok=True)
        staged_path.write_text(artifact["content"], encoding="utf-8")
        manifest_artifacts.append(
            {
                "artifactType": artifact.get("artifactType", "python-source"),
                "targetPath": target_path,
                "reason": artifact.get("reason", "AF-31/AF-32 validation artifact."),
            }
        )

    write_json_file(
        execution_root / "artifact_manifest.json",
        {
            "manifestVersion": "1.0",
            "artifacts": manifest_artifacts,
        },
    )


def read_report(execution_id: str) -> dict[str, Any]:
    return read_json_file(STAGING_ROOT / execution_id / "validation_apply_report.json")


def issue_codes(report: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for result in report.get("validation", {}).get("results", []):
        for issue in result.get("issues", []):
            code = issue.get("code")
            if isinstance(code, str):
                codes.append(code)
    return codes


def expect_exception_contains(action: Callable[[], None], expected_text: str) -> tuple[bool, str]:
    try:
        action()
    except Exception as exc:  # noqa: BLE001 - expected failure path.
        message = str(exc)
        if expected_text in message:
            return True, f"Found expected exception text: {expected_text}."
        return False, f"Expected exception containing {expected_text}, got: {message}"
    return False, f"Expected exception containing {expected_text}, but command completed successfully."


def cleanup() -> None:
    if STAGING_ROOT.exists():
        for path in STAGING_ROOT.glob(f"{TEST_PREFIX}*"):
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()

    if LIVE_SANDBOX_ROOT.exists():
        shutil.rmtree(LIVE_SANDBOX_ROOT)


def print_report(results: list[CheckResult]) -> None:
    print("AF-31 / AF-32 Validation Apply Engine verification")
    print("=" * 58)
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.name}")
        print(f"     {result.details}")
    print("=" * 58)
    passed_count = sum(1 for result in results if result.passed)
    print(f"Summary: {passed_count}/{len(results)} checks passed")


if __name__ == "__main__":
    main()
