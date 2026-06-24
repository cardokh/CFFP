from __future__ import annotations

import py_compile
import tempfile
from pathlib import Path
from typing import Any

from scripts.factory.validation_apply_engine.validation_apply_contracts import (
    ArtifactValidator,
    ValidationContext,
    ValidationIssue,
    ValidationResult,
)


class PathIntegrityValidator:
    """Validates target paths and staged file boundaries before any apply operation."""

    validator_id = "path-integrity-validator"

    def validate(self, context: ValidationContext) -> ValidationResult:
        issues: list[ValidationIssue] = []
        allowed_roots = _normalized_root_set(
            context.config.get("validation", {}).get("allowedTargetRoots", [])
        )
        denied_roots = _normalized_root_set(
            context.config.get("validation", {}).get("deniedTargetRoots", [])
        )

        for artifact in context.artifacts:
            target_path = artifact.target_path
            path = Path(target_path)

            if path.is_absolute():
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="ABSOLUTE_TARGET_PATH",
                        message="Artifact targetPath must be repository-relative.",
                        target_path=target_path,
                    )
                )

            if ".." in path.parts:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="TARGET_PATH_TRAVERSAL",
                        message="Artifact targetPath must not contain path traversal segments.",
                        target_path=target_path,
                    )
                )

            normalized_target = _normalize_path(target_path)
            if allowed_roots and not _is_under_any_root(normalized_target, allowed_roots):
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="TARGET_ROOT_NOT_ALLOWED",
                        message="Artifact targetPath is outside configured allowed target roots.",
                        target_path=target_path,
                        details={"allowedTargetRoots": sorted(allowed_roots)},
                    )
                )

            if _is_under_any_root(normalized_target, denied_roots):
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="TARGET_ROOT_DENIED",
                        message="Artifact targetPath is inside a configured denied target root.",
                        target_path=target_path,
                        details={"deniedTargetRoots": sorted(denied_roots)},
                    )
                )

            staged_path = artifact.staged_path.resolve()
            artifacts_root = context.artifacts_root.resolve()
            if artifacts_root != staged_path and artifacts_root not in staged_path.parents:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="STAGED_PATH_ESCAPES_WORKSPACE",
                        message="Artifact stagedPath escapes the Iteration 2 artifacts workspace.",
                        target_path=target_path,
                    )
                )

        return _result(self.validator_id, issues, {"artifactCount": len(context.artifacts)})


class ArtifactManifestValidator:
    """Validates manifest consistency, duplicate targets, and missing/orphan staged files."""

    validator_id = "artifact-manifest-validator"

    def validate(self, context: ValidationContext) -> ValidationResult:
        issues: list[ValidationIssue] = []
        validation_config = context.config.get("validation", {})

        if validation_config.get("requireManifestFile", True) and not context.manifest_path.exists():
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    code="MISSING_ARTIFACT_MANIFEST",
                    message="artifact_manifest.json is required in the staging execution workspace.",
                )
            )

        seen_targets: set[str] = set()
        duplicate_targets: set[str] = set()
        for artifact in context.artifacts:
            if artifact.target_path in seen_targets:
                duplicate_targets.add(artifact.target_path)
            seen_targets.add(artifact.target_path)
            if not artifact.staged_path.exists():
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="MISSING_STAGED_ARTIFACT",
                        message="Manifest references a staged artifact file that does not exist.",
                        target_path=artifact.target_path,
                    )
                )
            elif not artifact.staged_path.is_file():
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="STAGED_ARTIFACT_NOT_FILE",
                        message="Manifest references a staged artifact path that is not a file.",
                        target_path=artifact.target_path,
                    )
                )

        for duplicate_target in sorted(duplicate_targets):
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    code="DUPLICATE_TARGET_PATH",
                    message="Duplicate artifact targetPath detected in staged manifest.",
                    target_path=duplicate_target,
                )
            )

        if validation_config.get("failOnUnmanifestedStagedFiles", True):
            manifest_staged_paths = {artifact.staged_path.resolve() for artifact in context.artifacts}
            if context.artifacts_root.exists():
                for staged_file in sorted(path for path in context.artifacts_root.rglob("*") if path.is_file()):
                    if staged_file.resolve() not in manifest_staged_paths:
                        issues.append(
                            ValidationIssue(
                                severity="ERROR",
                                code="UNMANIFESTED_STAGED_FILE",
                                message="Staged artifact file exists but is not declared in artifact_manifest.json.",
                                target_path=_relative_to_root(context.artifacts_root, staged_file),
                            )
                        )

        return _result(self.validator_id, issues, {"artifactCount": len(context.artifacts)})


class DirectoryTargetProtectionValidator:
    """Prevents file/directory target collisions before apply can write to the repository."""

    validator_id = "directory-target-protection-validator"

    def validate(self, context: ValidationContext) -> ValidationResult:
        issues: list[ValidationIssue] = []
        normalized_targets = [_normalize_path(artifact.target_path) for artifact in context.artifacts]
        target_set = set(normalized_targets)
        collision_count = 0

        for artifact in context.artifacts:
            normalized_target = _normalize_path(artifact.target_path)
            target_path = (context.project_root / normalized_target).resolve()

            if artifact.target_path.replace("\\", "/").strip().endswith("/"):
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="DIRECTORY_TARGET_PATH",
                        message="Artifact targetPath must identify a file, not a directory-like path.",
                        target_path=artifact.target_path,
                    )
                )

            if target_path.exists() and target_path.is_dir():
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="TARGET_IS_DIRECTORY",
                        message="Artifact targetPath resolves to an existing directory and cannot be replaced by a file.",
                        target_path=artifact.target_path,
                    )
                )

            blocking_parent = _first_existing_file_parent(context.project_root, normalized_target)
            if blocking_parent is not None:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="PARENT_PATH_NOT_DIRECTORY",
                        message="Artifact targetPath has an existing parent path that is a file.",
                        target_path=artifact.target_path,
                        details={"blockingParent": _relative_to_root(context.project_root, blocking_parent)},
                    )
                )

            parent = Path(normalized_target).parent
            while parent.as_posix() not in {".", ""}:
                parent_target = parent.as_posix()
                if parent_target in target_set:
                    collision_count += 1
                    issues.append(
                        ValidationIssue(
                            severity="ERROR",
                            code="DIRECTORY_FILE_COLLISION",
                            message="Manifest contains target paths where one artifact would be a parent directory of another.",
                            target_path=artifact.target_path,
                            details={"collidingTarget": parent_target},
                        )
                    )
                parent = parent.parent

        return _result(
            self.validator_id,
            issues,
            {
                "artifactCount": len(context.artifacts),
                "directoryFileCollisionCount": collision_count,
            },
        )


class PythonCompileValidator:
    """Runs native Python compilation checks for staged Python files."""

    validator_id = "python-compile-validator"

    def validate(self, context: ValidationContext) -> ValidationResult:
        if not context.config.get("validation", {}).get("pythonCompileEnabled", True):
            return ValidationResult(
                validator_id=self.validator_id,
                status="SKIPPED",
                metadata={"reason": "pythonCompileEnabled is false"},
            )

        issues: list[ValidationIssue] = []
        checked_count = 0
        for artifact in context.artifacts:
            if not artifact.target_path.endswith(".py"):
                continue
            if not artifact.staged_path.is_file():
                continue
            checked_count += 1
            try:
                with tempfile.TemporaryDirectory(prefix="cffp_pycompile_") as cache_dir:
                    compiled_path = Path(cache_dir) / "artifact.pyc"
                    py_compile.compile(
                        str(artifact.staged_path),
                        cfile=str(compiled_path),
                        doraise=True,
                    )
            except py_compile.PyCompileError as exc:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="PYTHON_COMPILE_FAILED",
                        message="Staged Python artifact failed py_compile validation.",
                        target_path=artifact.target_path,
                        details={"error": str(exc)},
                    )
                )

        return _result(self.validator_id, issues, {"pythonFilesChecked": checked_count})


class StyleSanityValidator:
    """Applies lightweight formatting sanity checks to staged text files."""

    validator_id = "style-sanity-validator"

    def validate(self, context: ValidationContext) -> ValidationResult:
        if not context.config.get("validation", {}).get("styleValidationEnabled", True):
            return ValidationResult(
                validator_id=self.validator_id,
                status="SKIPPED",
                metadata={"reason": "styleValidationEnabled is false"},
            )

        style_rules = context.config.get("validation", {}).get("styleRules", {})
        require_final_newline = style_rules.get("requireFinalNewline", True)
        disallow_trailing_whitespace = style_rules.get("disallowTrailingWhitespace", True)
        disallow_tabs = style_rules.get("disallowTabCharacters", False)
        max_line_length = int(style_rules.get("maxLineLength", 160))

        issues: list[ValidationIssue] = []
        checked_count = 0
        for artifact in context.artifacts:
            if not artifact.staged_path.is_file():
                continue
            if _is_probably_binary(artifact.staged_path):
                continue
            checked_count += 1
            try:
                content = artifact.staged_path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="TEXT_DECODING_FAILED",
                        message="Staged artifact could not be decoded as UTF-8 text.",
                        target_path=artifact.target_path,
                        details={"error": str(exc)},
                    )
                )
                continue

            if require_final_newline and content and not content.endswith("\n"):
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        code="MISSING_FINAL_NEWLINE",
                        message="Text artifact must end with a newline.",
                        target_path=artifact.target_path,
                    )
                )

            for line_number, line in enumerate(content.splitlines(), start=1):
                if disallow_trailing_whitespace and line.rstrip(" \t") != line:
                    issues.append(
                        ValidationIssue(
                            severity="ERROR",
                            code="TRAILING_WHITESPACE",
                            message="Line contains trailing whitespace.",
                            target_path=artifact.target_path,
                            details={"line": line_number},
                        )
                    )
                if disallow_tabs and "\t" in line:
                    issues.append(
                        ValidationIssue(
                            severity="ERROR",
                            code="TAB_CHARACTER",
                            message="Line contains a tab character.",
                            target_path=artifact.target_path,
                            details={"line": line_number},
                        )
                    )
                if max_line_length > 0 and len(line) > max_line_length:
                    issues.append(
                        ValidationIssue(
                            severity="ERROR",
                            code="LINE_TOO_LONG",
                            message="Line exceeds configured maximum length.",
                            target_path=artifact.target_path,
                            details={"line": line_number, "length": len(line), "maxLineLength": max_line_length},
                        )
                    )

        return _result(self.validator_id, issues, {"textFilesChecked": checked_count})


class OverwritePolicyValidator:
    """Validates configured overwrite policy before apply can run."""

    validator_id = "overwrite-policy-validator"

    def validate(self, context: ValidationContext) -> ValidationResult:
        apply_config = context.config.get("apply", {})
        overwrite_policy = apply_config.get("overwritePolicy", "FAIL")
        if overwrite_policy not in {"FAIL", "BACKUP"}:
            return ValidationResult(
                validator_id=self.validator_id,
                status="FAILED",
                issues=[
                    ValidationIssue(
                        severity="ERROR",
                        code="UNSUPPORTED_OVERWRITE_POLICY",
                        message="overwritePolicy must be either FAIL or BACKUP for Iteration 3.",
                        details={"overwritePolicy": overwrite_policy},
                    )
                ],
            )

        issues: list[ValidationIssue] = []
        existing_targets = []
        for artifact in context.artifacts:
            target_path = (context.project_root / artifact.target_path).resolve()
            if target_path.exists():
                existing_targets.append(artifact.target_path)
                if overwrite_policy == "FAIL":
                    issues.append(
                        ValidationIssue(
                            severity="ERROR",
                            code="OVERWRITE_CONFLICT",
                            message="Target file already exists and overwritePolicy is FAIL.",
                            target_path=artifact.target_path,
                        )
                    )

        return _result(
            self.validator_id,
            issues,
            {
                "overwritePolicy": overwrite_policy,
                "existingTargetCount": len(existing_targets),
                "existingTargets": existing_targets,
            },
        )


class ValidationPipeline:
    """Sequential validator chain used by the Validation & Apply Engine."""

    def __init__(self, validators: list[ArtifactValidator]):
        self._validators = validators

    def validate(self, context: ValidationContext) -> list[ValidationResult]:
        return [validator.validate(context) for validator in self._validators]


def default_validation_pipeline() -> ValidationPipeline:
    return ValidationPipeline(
        validators=[
            ArtifactManifestValidator(),
            PathIntegrityValidator(),
            DirectoryTargetProtectionValidator(),
            PythonCompileValidator(),
            StyleSanityValidator(),
            OverwritePolicyValidator(),
        ]
    )


def _first_existing_file_parent(project_root: Path, normalized_target: str) -> Path | None:
    current = project_root.resolve()
    parts = Path(normalized_target).parts[:-1]
    for part in parts:
        current = current / part
        if current.exists() and not current.is_dir():
            return current
    return None


def _result(validator_id: str, issues: list[ValidationIssue], metadata: dict[str, Any]) -> ValidationResult:
    return ValidationResult(
        validator_id=validator_id,
        status="FAILED" if issues else "PASSED",
        issues=issues,
        metadata=metadata,
    )


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _normalized_root_set(roots: list[str]) -> set[str]:
    return {_normalize_path(root) for root in roots if isinstance(root, str) and root.strip()}


def _is_under_any_root(target_path: str, roots: set[str]) -> bool:
    return any(target_path == root or target_path.startswith(f"{root}/") for root in roots)


def _relative_to_root(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _is_probably_binary(path: Path) -> bool:
    return path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".pyc"}
