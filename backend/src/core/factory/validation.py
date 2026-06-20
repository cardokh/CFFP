"""Validation helpers for controlled local artifact writing."""

from __future__ import annotations

from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when a factory validation step fails."""


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

    if not text.strip():
        raise ValidationError("Generated text is empty.")
    if len(text) > max_characters:
        raise ValidationError(
            f"Generated text is too large: {len(text)} characters. Limit: {max_characters}."
        )
    blocked_terms = ("GEMINI_API_KEY=", "API Key:", "AQ.")
    for blocked_term in blocked_terms:
        if blocked_term in text:
            raise ValidationError(f"Generated text contains a blocked secret-like term: {blocked_term}")


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
