"""Repository context data models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RepositoryContextConfig:
    """Configuration for repository context collection."""

    enabled: bool
    include_patterns: tuple[str, ...]
    exclude_patterns: tuple[str, ...]
    max_files: int
    max_file_characters: int


@dataclass(frozen=True)
class RepositoryContextFile:
    """One repository file included in a context package."""

    path: str
    size_bytes: int
    content: str
    truncated: bool


@dataclass(frozen=True)
class RepositoryContextPackage:
    """Repository context package passed to prompts and reports."""

    enabled: bool
    root: str
    files: tuple[RepositoryContextFile, ...]
    skipped_files: tuple[str, ...]
    include_patterns: tuple[str, ...]
    exclude_patterns: tuple[str, ...]
    max_files: int
    max_file_characters: int

    def to_report_snapshot(self) -> dict[str, Any]:
        """Return a JSON-serializable repository context snapshot."""

        return {
            "enabled": self.enabled,
            "root": self.root,
            "file_count": len(self.files),
            "skipped_file_count": len(self.skipped_files),
            "include_patterns": list(self.include_patterns),
            "exclude_patterns": list(self.exclude_patterns),
            "max_files": self.max_files,
            "max_file_characters": self.max_file_characters,
            "files": [
                {
                    "path": context_file.path,
                    "size_bytes": context_file.size_bytes,
                    "characters": len(context_file.content),
                    "truncated": context_file.truncated,
                }
                for context_file in self.files
            ],
            "skipped_files": list(self.skipped_files),
        }

    def to_prompt_text(self) -> str:
        """Return a compact deterministic text representation."""

        if not self.enabled:
            return "Repository context collection is disabled."
        if not self.files:
            return "Repository context collection found no matching files."

        sections: list[str] = [
            "Repository Context",
            f"Root: {self.root}",
            f"Included files: {len(self.files)}",
            "",
        ]

        for context_file in self.files:
            truncation_note = " (truncated)" if context_file.truncated else ""
            sections.extend(
                [
                    f"--- FILE: {context_file.path}{truncation_note} ---",
                    context_file.content.rstrip(),
                    "",
                ]
            )

        return "\n".join(sections).strip()
