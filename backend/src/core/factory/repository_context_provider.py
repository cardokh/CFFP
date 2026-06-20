"""Filesystem implementation of repository context collection."""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from .constants import TEXT_FILE_EXTENSIONS
from .repository_context_models import (
    RepositoryContextConfig,
    RepositoryContextFile,
    RepositoryContextPackage,
)


class FilesystemRepositoryContextProvider:
    """Configuration-driven repository context provider."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()

    def collect_context(self, config: RepositoryContextConfig) -> RepositoryContextPackage:
        """Collect a deterministic repository context package."""

        if not config.enabled:
            return self._empty_package(config)

        included_files: list[RepositoryContextFile] = []
        skipped_files: list[str] = []

        for candidate_path in sorted(self.project_root.rglob("*")):
            if self._should_ignore_candidate(candidate_path):
                continue

            relative_path = self._relative_path(candidate_path)
            if not self._should_include(relative_path, candidate_path, config):
                skipped_files.append(relative_path)
                continue

            if len(included_files) >= config.max_files:
                skipped_files.append(relative_path)
                continue

            included_files.append(
                self._read_context_file(candidate_path, relative_path, config.max_file_characters)
            )

        return RepositoryContextPackage(
            enabled=True,
            root=str(self.project_root),
            files=tuple(included_files),
            skipped_files=tuple(skipped_files),
            include_patterns=config.include_patterns,
            exclude_patterns=config.exclude_patterns,
            max_files=config.max_files,
            max_file_characters=config.max_file_characters,
        )

    def _empty_package(self, config: RepositoryContextConfig) -> RepositoryContextPackage:
        return RepositoryContextPackage(
            enabled=False,
            root=str(self.project_root),
            files=(),
            skipped_files=(),
            include_patterns=config.include_patterns,
            exclude_patterns=config.exclude_patterns,
            max_files=config.max_files,
            max_file_characters=config.max_file_characters,
        )

    @staticmethod
    def _should_ignore_candidate(candidate_path: Path) -> bool:
        return not candidate_path.is_file()

    def _should_include(
        self,
        relative_path: str,
        candidate_path: Path,
        config: RepositoryContextConfig,
    ) -> bool:
        if not self._matches_any(relative_path, config.include_patterns):
            return False
        if self._matches_any(relative_path, config.exclude_patterns):
            return False
        return candidate_path.suffix.lower() in TEXT_FILE_EXTENSIONS

    def _relative_path(self, candidate_path: Path) -> str:
        resolved_candidate = candidate_path.resolve()
        try:
            return resolved_candidate.relative_to(self.project_root).as_posix()
        except ValueError as exc:
            raise ValueError(f"Path must be inside project root: {resolved_candidate}") from exc

    @staticmethod
    def _read_context_file(
        candidate_path: Path,
        relative_path: str,
        max_file_characters: int,
    ) -> RepositoryContextFile:
        content = candidate_path.read_text(encoding="utf-8", errors="replace")
        truncated = len(content) > max_file_characters
        if truncated:
            content = content[:max_file_characters]

        return RepositoryContextFile(
            path=relative_path,
            size_bytes=candidate_path.stat().st_size,
            content=content,
            truncated=truncated,
        )

    @staticmethod
    def _matches_any(relative_path: str, patterns: tuple[str, ...]) -> bool:
        return any(fnmatch(relative_path, pattern) for pattern in patterns)
