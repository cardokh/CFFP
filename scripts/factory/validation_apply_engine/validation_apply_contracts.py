from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class StagedArtifact:
    """Single untrusted artifact staged by the AI Generation Engine."""

    artifact_type: str
    target_path: str
    staged_path: Path
    content_sha256: str
    size_bytes: int
    line_count: int
    reason: str = ""

    def to_report_dict(self, project_root: Path) -> dict[str, Any]:
        staged_path = self.staged_path.resolve()
        try:
            relative_staged_path = staged_path.relative_to(project_root.resolve()).as_posix()
        except ValueError:
            relative_staged_path = staged_path.as_posix()

        return {
            "artifactType": self.artifact_type,
            "targetPath": self.target_path,
            "stagedPath": relative_staged_path,
            "contentSha256": self.content_sha256,
            "sizeBytes": self.size_bytes,
            "lineCount": self.line_count,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ValidationIssue:
    """Programmatic validation issue reported by a validator."""

    severity: str
    code: str
    message: str
    target_path: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationResult:
    """Result emitted by one validation stage."""

    validator_id: str
    status: str
    issues: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "validatorId": self.validator_id,
            "status": self.status,
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ValidationContext:
    """Immutable validation context shared by all validator implementations."""

    project_root: Path
    execution_root: Path
    artifacts_root: Path
    manifest_path: Path
    artifacts: list[StagedArtifact]
    config: dict[str, Any]


class ArtifactValidator(Protocol):
    """Replaceable validation stage for staged Automation Factory artifacts."""

    validator_id: str

    def validate(self, context: ValidationContext) -> ValidationResult:
        """Validate staged artifacts and return a structured result."""
