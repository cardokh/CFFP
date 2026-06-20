"""Validation provider implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .validation import (
    validate_artifact_path,
    validate_generated_text,
    validate_written_artifact,
)


@dataclass(frozen=True)
class StandardValidationProvider:
    """Default Factory validation provider."""

    def validate_generated_text(self, generated_text: str, max_characters: int) -> None:
        validate_generated_text(generated_text, max_characters)

    def validate_artifact_path(
        self,
        output_dir: Path,
        artifact_path: Path,
        allowed_extensions: tuple[str, ...],
    ) -> None:
        validate_artifact_path(output_dir, artifact_path, allowed_extensions)

    def validate_written_artifact(self, artifact_path: Path) -> dict[str, object]:
        return validate_written_artifact(artifact_path)
