"""Payload-driven local context collection for Factory tasks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .task_prompt_models import ContextFileSnapshot, TaskContextBundle

DEFAULT_CONTEXT_TARGETS_KEY = "context_targets"
DEFAULT_MAX_FILE_CHARACTERS = 6000
DEFAULT_MAX_TOTAL_CHARACTERS = 20000


@dataclass(frozen=True)
class LocalTaskContextCollector:
    """Collects local text context from paths declared in task payload."""

    project_root: Path

    def collect(self, payload: dict[str, Any]) -> TaskContextBundle:
        """Collect text context files configured by the task payload."""

        targets = self._read_targets(payload)
        max_file_characters = int(payload.get("max_file_characters", DEFAULT_MAX_FILE_CHARACTERS))
        max_total_characters = int(payload.get("max_total_characters", DEFAULT_MAX_TOTAL_CHARACTERS))

        files: list[ContextFileSnapshot] = []
        consumed_characters = 0
        for target in targets:
            for file_path in self._iter_target_files(target):
                remaining = max_total_characters - consumed_characters
                if remaining <= 0:
                    return TaskContextBundle(files=tuple(files))

                snapshot = self._read_snapshot(file_path, min(max_file_characters, remaining))
                consumed_characters += len(snapshot.content)
                files.append(snapshot)

        return TaskContextBundle(files=tuple(files))

    def _read_targets(self, payload: dict[str, Any]) -> tuple[str, ...]:
        raw_targets = payload.get(DEFAULT_CONTEXT_TARGETS_KEY, ())
        if raw_targets in (None, ""):
            return ()
        if isinstance(raw_targets, str):
            return (raw_targets,)
        if not isinstance(raw_targets, (list, tuple)):
            raise ValueError("Task payload context_targets must be a string or list of strings.")
        return tuple(str(target) for target in raw_targets)

    def _iter_target_files(self, target: str) -> tuple[Path, ...]:
        resolved_target = self._resolve_project_path(target)
        if resolved_target.is_file():
            return (resolved_target,)
        if resolved_target.is_dir():
            return tuple(sorted(path for path in resolved_target.rglob("*") if path.is_file()))
        raise ValueError(f"Context target does not exist: {target}")

    def _resolve_project_path(self, relative_path: str) -> Path:
        candidate = (self.project_root / relative_path).resolve()
        try:
            candidate.relative_to(self.project_root.resolve())
        except ValueError as exc:
            raise ValueError(f"Context target must stay inside project root: {relative_path}") from exc
        return candidate

    def _read_snapshot(self, file_path: Path, max_characters: int) -> ContextFileSnapshot:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        truncated = len(content) > max_characters
        if truncated:
            content = content[:max_characters]
        return ContextFileSnapshot(
            path=file_path.relative_to(self.project_root.resolve()).as_posix(),
            content=content,
            truncated=truncated,
        )
