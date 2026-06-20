"""Repository context provider factory implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .contracts import RepositoryContextProvider
from .repository_context_provider import FilesystemRepositoryContextProvider


@dataclass(frozen=True)
class FilesystemRepositoryContextProviderFactory:
    """Creates filesystem repository context providers."""

    def create_provider(self, project_root: Path) -> RepositoryContextProvider:
        """Create a repository context provider for the project root."""

        return FilesystemRepositoryContextProvider(project_root)
