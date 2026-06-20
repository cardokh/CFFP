"""Controlled artifact writer implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import ValidationProvider
from .models import AutomationTaskDefinition


@dataclass(frozen=True)
class FilesystemArtifactWriter:
    """Writes generated artifacts to configured output locations."""

    validation_provider: ValidationProvider

    def write_artifact(
        self,
        task_definition: AutomationTaskDefinition,
        generated_text: str,
    ) -> dict[str, object]:
        artifact_definition = task_definition.artifact
        artifact_definition.output_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifact_definition.output_dir / artifact_definition.filename

        self.validation_provider.validate_artifact_path(
            artifact_definition.output_dir,
            artifact_path,
            artifact_definition.allowed_extensions,
        )
        artifact_path.write_text(generated_text, encoding="utf-8")
        return self.validation_provider.validate_written_artifact(artifact_path)
