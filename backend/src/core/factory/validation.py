"""Validation helpers for controlled Factory output."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when a factory validation step fails."""


@dataclass(frozen=True)
class FactoryValidationResult:
    """Structured result for Factory business validation."""

    passed: bool
    checks: tuple[dict[str, object], ...]
    message: str

    def to_dict(self) -> dict[str, object]:
        """Return a serializable validation result."""

        return {
            "passed": self.passed,
            "checks": list(self.checks),
            "message": self.message,
        }


@dataclass(frozen=True)
class FactoryOutputValidator:
    """Business validator for generated Factory artifacts."""

    max_characters: int = 200_000

    def validate_artifact_text(self, artifact_text: str | None) -> FactoryValidationResult:
        """Validate generated artifact content before persistence."""

        checks: list[dict[str, object]] = []
        text = artifact_text or ""

        has_content = bool(text.strip())
        checks.append({"name": "not_empty", "passed": has_content})
        if not has_content:
            return FactoryValidationResult(False, tuple(checks), "Generated artifact text is empty.")

        size_allowed = len(text) <= self.max_characters
        checks.append(
            {
                "name": "max_characters",
                "passed": size_allowed,
                "actual": len(text),
                "limit": self.max_characters,
            }
        )
        if not size_allowed:
            return FactoryValidationResult(
                False,
                tuple(checks),
                f"Generated artifact text is too large: {len(text)} characters.",
            )

        blocked_terms = ("GEMINI_API_KEY=", "OPENAI_API_KEY=", "API Key:", "AQ.")
        blocked_hits = [term for term in blocked_terms if term in text]
        checks.append({"name": "no_secret_like_terms", "passed": not blocked_hits, "hits": blocked_hits})
        if blocked_hits:
            return FactoryValidationResult(
                False,
                tuple(checks),
                "Generated artifact text contains blocked secret-like terms.",
            )

        error_markers = (
            "traceback (most recent call last)",
            "uncaught exception",
            "authentication failed",
            "permission denied",
        )
        normalized = text.lower()
        error_hits = [marker for marker in error_markers if marker in normalized]
        checks.append({"name": "no_error_markers", "passed": not error_hits, "hits": error_hits})
        if error_hits:
            return FactoryValidationResult(
                False,
                tuple(checks),
                "Generated artifact text contains error markers.",
            )

        markdown_like = "#" in text or "```" in text or len(text.splitlines()) >= 2
        checks.append({"name": "structured_text", "passed": markdown_like})
        if not markdown_like:
            return FactoryValidationResult(
                False,
                tuple(checks),
                "Generated artifact text does not look structured enough to persist.",
            )

        return FactoryValidationResult(True, tuple(checks), "Generated artifact text passed validation.")


def ensure_child_path(parent: Path, child: Path) -> None:
    """Ensure that child is inside parent."""

    resolved_parent = parent.resolve()
    resolved_child = child.resolve()
    try:
        resolved_child.relative_to(resolved_parent)
    except ValueError as exc:
        raise ValidationError(f"Path is outside allowed directory: {resolved_child}") from exc


def validate_artifact_path(output_dir: Path, artifact_path: Path, allowed_extensions: tuple[str, ...]) -> None:
    """Validate that the artifact path is safe and has an allowed extension."""

    ensure_child_path(output_dir, artifact_path)
    if artifact_path.suffix not in allowed_extensions:
        raise ValidationError(
            f"Artifact extension '{artifact_path.suffix}' is not allowed. "
            f"Allowed extensions: {', '.join(allowed_extensions)}"
        )


def validate_generated_text(text: str, max_characters: int) -> None:
    """Validate generated text before writing it to disk."""

    result = FactoryOutputValidator(max_characters=max_characters).validate_artifact_text(text)
    if not result.passed:
        raise ValidationError(result.message)


def validate_written_artifact(artifact_path: Path) -> dict[str, object]:
    """Validate that the written artifact exists and contains content."""

    if not artifact_path.exists():
        raise ValidationError(f"Artifact was not written: {artifact_path}")
    if not artifact_path.is_file():
        raise ValidationError(f"Artifact path is not a file: {artifact_path}")

    size_bytes = artifact_path.stat().st_size
    if size_bytes <= 0:
        raise ValidationError(f"Artifact is empty: {artifact_path}")

    return {
        "path": str(artifact_path),
        "size_bytes": size_bytes,
        "exists": True,
    }
