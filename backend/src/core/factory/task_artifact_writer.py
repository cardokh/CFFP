"""Factory runtime artifact writing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .validation import ensure_child_path


@dataclass(frozen=True)
class FactoryTaskArtifactRecord:
    """Metadata for one persisted Factory execution artifact."""

    path: str
    size_bytes: int

    def to_dict(self) -> dict[str, object]:
        """Return a serializable artifact record."""

        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class FactoryTaskArtifactWriter:
    """Writes generated Factory artifacts outside the source tree."""

    output_root: Path

    def write_artifact(
        self,
        *,
        execution_id: str,
        task_id: str,
        artifact_text: str,
        filename: str | None = None,
    ) -> FactoryTaskArtifactRecord:
        """Write one generated artifact and return metadata."""

        safe_task_id = _safe_path_segment(task_id)
        safe_filename = filename or "generated_artifact.md"
        execution_dir = self.output_root / safe_task_id / execution_id
        execution_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = execution_dir / _safe_filename(safe_filename)
        ensure_child_path(self.output_root, artifact_path)
        artifact_path.write_text(artifact_text, encoding="utf-8")
        return FactoryTaskArtifactRecord(
            path=str(artifact_path),
            size_bytes=artifact_path.stat().st_size,
        )


def _safe_path_segment(value: str) -> str:
    cleaned = "".join(character if character.isalnum() or character in ("-", "_") else "-" for character in value)
    return cleaned.strip("-") or "factory-task"


def _safe_filename(value: str) -> str:
    candidate = Path(value).name
    if not candidate:
        return "generated_artifact.md"
    if candidate.startswith("."):
        candidate = candidate.lstrip(".") or "generated_artifact.md"
    return candidate
