from __future__ import annotations

import hashlib
import json
import shutil
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.validation_apply_engine.validation_apply_contracts import (  # noqa: E402
    StagedArtifact,
    ValidationContext,
    ValidationResult,
)
from scripts.factory.validation_apply_engine.validation_apply_validators import (  # noqa: E402
    default_validation_pipeline,
)
from scripts.shared.base_script import BaseScript  # noqa: E402
from scripts.shared.script_json_utils import read_json_file, write_json_file  # noqa: E402


class ValidationApplyEngine(BaseScript):
    """
    Validates untrusted staged artifacts and optionally applies them to live source.

    Iteration 3 reads only the isolated Iteration 2 staging workspace. Artifacts are
    treated as untrusted until every validator reports PASSED. Apply is disabled by
    default and only runs when config apply.mode is explicitly validate-and-apply.
    """

    VALIDATE_ONLY = "validate-only"
    VALIDATE_AND_APPLY = "validate-and-apply"

    def __init__(self):
        super().__init__(__file__)

    def run(self) -> None:
        started_at = self._utc_now()
        start_counter = perf_counter()

        execution_root = self._resolve_execution_root()
        artifacts_root = execution_root / "artifacts"
        manifest_path = execution_root / "artifact_manifest.json"
        report_path = execution_root / self.config.get("outputs", {}).get(
            "reportFileName",
            "validation_apply_report.json",
        )

        manifest = self._read_manifest(manifest_path)
        artifacts = self._load_staged_artifacts(manifest, artifacts_root)
        context = ValidationContext(
            project_root=self.project_root,
            execution_root=execution_root,
            artifacts_root=artifacts_root,
            manifest_path=manifest_path,
            artifacts=artifacts,
            config=self.config,
        )

        validation_results = default_validation_pipeline().validate(context)
        validation_status = self._combined_validation_status(validation_results)
        apply_status = "SKIPPED"
        applied_files: list[dict[str, Any]] = []
        apply_errors: list[dict[str, Any]] = []

        mode = self.config.get("apply", {}).get("mode", self.VALIDATE_ONLY)
        if mode not in {self.VALIDATE_ONLY, self.VALIDATE_AND_APPLY}:
            validation_status = "FAILED"
            apply_status = "SKIPPED"
            apply_errors.append(
                {
                    "code": "UNSUPPORTED_APPLY_MODE",
                    "message": "apply.mode must be validate-only or validate-and-apply.",
                    "mode": mode,
                }
            )
        elif mode == self.VALIDATE_AND_APPLY and validation_status == "PASSED":
            apply_status, applied_files, apply_errors = self._apply_artifacts(context)
        elif mode == self.VALIDATE_AND_APPLY:
            apply_status = "BLOCKED_BY_VALIDATION"

        finished_at = self._utc_now()
        elapsed_ms = round((perf_counter() - start_counter) * 1000, 3)
        report = self._build_report(
            started_at=started_at,
            finished_at=finished_at,
            elapsed_ms=elapsed_ms,
            execution_root=execution_root,
            artifacts_root=artifacts_root,
            manifest_path=manifest_path,
            report_path=report_path,
            manifest=manifest,
            artifacts=artifacts,
            validation_results=validation_results,
            validation_status=validation_status,
            apply_mode=mode,
            apply_status=apply_status,
            applied_files=applied_files,
            apply_errors=apply_errors,
        )
        write_json_file(report_path, report)

        print(
            f"PASS {self.script_name}: validation={validation_status}, apply={apply_status}, "
            f"artifacts={len(artifacts)}, report={self.to_project_relative_path(report_path)}"
        )

    def _resolve_execution_root(self) -> Path:
        inputs_config = self.config.get("inputs", {})
        staging_root = self._resolve_project_relative_path(
            inputs_config.get("stagingRoot", ".ccore_workspace/staging")
        )
        execution_id = inputs_config.get("executionId")

        if not isinstance(execution_id, str) or not execution_id.strip():
            raise ValueError(
                "EXECUTION_ID_REQUIRED: inputs.executionId is required. "
                "Implicit latest execution selection is disabled."
            )

        execution_root = self._safe_child(staging_root, execution_id.strip())
        if not execution_root.exists():
            raise FileNotFoundError(
                f"EXECUTION_NOT_FOUND: configured staging execution does not exist: {execution_root}"
            )
        if not execution_root.is_dir():
            raise NotADirectoryError(
                f"EXECUTION_ROOT_NOT_DIRECTORY: configured staging execution is not a directory: {execution_root}"
            )
        return execution_root

    def _read_manifest(self, manifest_path: Path) -> dict[str, Any]:
        if not manifest_path.exists():
            if self.config.get("validation", {}).get("requireManifestFile", True):
                raise FileNotFoundError(f"artifact_manifest.json not found: {manifest_path}")
            return {"manifestVersion": None, "artifacts": []}
        manifest = read_json_file(manifest_path)
        if not isinstance(manifest, dict):
            raise ValueError("artifact_manifest.json root must be an object.")
        artifacts = manifest.get("artifacts", [])
        if not isinstance(artifacts, list):
            raise ValueError("artifact_manifest.json field artifacts must be a list.")
        return manifest

    def _load_staged_artifacts(self, manifest: dict[str, Any], artifacts_root: Path) -> list[StagedArtifact]:
        artifacts: list[StagedArtifact] = []
        for index, artifact in enumerate(manifest.get("artifacts", []), start=1):
            if not isinstance(artifact, dict):
                raise ValueError(f"Manifest artifact {index} must be an object.")
            target_path = self._normalize_target_path(artifact.get("targetPath"), index)
            staged_path = self._safe_child(artifacts_root, target_path)

            content = staged_path.read_text(encoding="utf-8") if staged_path.exists() and staged_path.is_file() else ""
            artifacts.append(
                StagedArtifact(
                    artifact_type=str(artifact.get("artifactType", "unspecified")),
                    target_path=target_path,
                    staged_path=staged_path,
                    content_sha256=self._sha256(content),
                    size_bytes=len(content.encode("utf-8")),
                    line_count=self._line_count(content),
                    reason=str(artifact.get("reason", "")),
                )
            )
        return artifacts

    def _apply_artifacts(
        self,
        context: ValidationContext,
    ) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
        applied_files: list[dict[str, Any]] = []
        apply_errors: list[dict[str, Any]] = []
        overwrite_policy = context.config.get("apply", {}).get("overwritePolicy", "FAIL")
        backup_root = context.execution_root / context.config.get("apply", {}).get(
            "backupDirectoryName",
            "apply_backups",
        )

        for artifact in context.artifacts:
            target_path = self._safe_child(context.project_root, artifact.target_path)
            try:
                backup_path = None
                if target_path.exists() and target_path.is_dir():
                    raise IsADirectoryError(f"TARGET_IS_DIRECTORY: target path is a directory: {target_path}")
                if target_path.parent.exists() and not target_path.parent.is_dir():
                    raise NotADirectoryError(
                        f"PARENT_PATH_NOT_DIRECTORY: target parent is not a directory: {target_path.parent}"
                    )
                if target_path.exists():
                    if overwrite_policy == "FAIL":
                        raise FileExistsError(f"Target exists and overwritePolicy is FAIL: {target_path}")
                    if overwrite_policy == "BACKUP":
                        backup_path = self._safe_child(backup_root, artifact.target_path)
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(target_path, backup_path)

                target_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = target_path.with_name(f".{target_path.name}.cffp_apply_tmp")
                shutil.copy2(artifact.staged_path, temp_path)
                temp_path.replace(target_path)

                applied_files.append(
                    {
                        "targetPath": artifact.target_path,
                        "sourcePath": self.to_project_relative_path(artifact.staged_path),
                        "appliedPath": self.to_project_relative_path(target_path),
                        "backupPath": self.to_project_relative_path(backup_path) if backup_path else None,
                        "sha256": artifact.content_sha256,
                        "sizeBytes": artifact.size_bytes,
                    }
                )
            except Exception as exc:  # noqa: BLE001 - report and stop controlled apply sequence.
                apply_errors.append(
                    {
                        "targetPath": artifact.target_path,
                        "code": "APPLY_FAILED",
                        "message": str(exc),
                    }
                )
                return "FAILED", applied_files, apply_errors

        return "APPLIED", applied_files, apply_errors

    def _combined_validation_status(self, validation_results: list[ValidationResult]) -> str:
        if any(result.status == "FAILED" for result in validation_results):
            return "FAILED"
        return "PASSED"

    def _build_report(
        self,
        *,
        started_at: str,
        finished_at: str,
        elapsed_ms: float,
        execution_root: Path,
        artifacts_root: Path,
        manifest_path: Path,
        report_path: Path,
        manifest: dict[str, Any],
        artifacts: list[StagedArtifact],
        validation_results: list[ValidationResult],
        validation_status: str,
        apply_mode: str,
        apply_status: str,
        applied_files: list[dict[str, Any]],
        apply_errors: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "reportType": "validation-apply-engine",
            "reportVersion": "3.0",
            "status": validation_status if apply_status in {"SKIPPED", "APPLIED"} else "FAILED",
            "timestamps": {
                "startedAt": started_at,
                "finishedAt": finished_at,
                "elapsedMs": elapsed_ms,
            },
            "workspace": {
                "executionRoot": self.to_project_relative_path(execution_root),
                "artifactsRoot": self.to_project_relative_path(artifacts_root),
                "manifestPath": self.to_project_relative_path(manifest_path),
                "reportPath": self.to_project_relative_path(report_path),
            },
            "inputIsolation": {
                "allowedInputRoot": self.to_project_relative_path(execution_root),
                "readsMasterContext": False,
                "readsOriginalSpecificationFiles": False,
            },
            "manifest": {
                "manifestVersion": manifest.get("manifestVersion"),
                "artifactCount": len(artifacts),
                "manifestSha256": self._sha256(json.dumps(manifest, sort_keys=True, indent=4)),
            },
            "validation": {
                "status": validation_status,
                "results": [result.to_dict() for result in validation_results],
            },
            "apply": {
                "mode": apply_mode,
                "status": apply_status,
                "overwritePolicy": self.config.get("apply", {}).get("overwritePolicy", "FAIL"),
                "appliedFiles": applied_files,
                "errors": apply_errors,
            },
            "artifacts": [artifact.to_report_dict(self.project_root) for artifact in artifacts],
            "safety": {
                "applyRequiresValidationPassed": True,
                "liveSourceWriteAllowedBeforeValidation": False,
                "pathTraversalProtection": True,
                "workspaceBoundaryProtection": True,
                "defaultMode": "validate-only",
            },
        }

    def _resolve_project_relative_path(self, relative_path: str) -> Path:
        path = Path(relative_path)
        if path.is_absolute():
            raise ValueError(f"Configured path must be project-relative: {relative_path}")
        if ".." in path.parts:
            raise ValueError(f"Configured path must not contain path traversal: {relative_path}")
        return (self.project_root / path).resolve()

    def _safe_child(self, root: Path, relative_path: str) -> Path:
        normalized_relative_path = self._normalize_path_string(relative_path)
        root_resolved = root.resolve()
        candidate = (root_resolved / normalized_relative_path).resolve()
        if root_resolved != candidate and root_resolved not in candidate.parents:
            raise ValueError(f"Path escapes configured root: {relative_path}")
        return candidate

    def _normalize_target_path(self, value: Any, artifact_index: int) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Manifest artifact {artifact_index} must define a non-empty targetPath string.")
        raw_target_path = value.replace("\\", "/").strip()
        if raw_target_path.endswith("/"):
            raise ValueError(
                f"Manifest artifact {artifact_index} targetPath must identify a file, not a directory-like path."
            )
        target_path = self._normalize_path_string(value)
        path = Path(target_path)
        if path.is_absolute():
            raise ValueError(f"Manifest artifact {artifact_index} targetPath must be repository-relative.")
        if ".." in path.parts:
            raise ValueError(f"Manifest artifact {artifact_index} targetPath must not contain path traversal.")
        return target_path

    def _normalize_path_string(self, value: str) -> str:
        path = value.replace("\\", "/").strip("/")
        if not path:
            raise ValueError("Path value must not be empty.")
        return path

    def _sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _line_count(self, content: str) -> int:
        if content == "":
            return 0
        return content.count("\n") + (0 if content.endswith("\n") else 1)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    ValidationApplyEngine().run()
