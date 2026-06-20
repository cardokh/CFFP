"""Repository context configuration builder."""

from __future__ import annotations

from typing import Any

from .constants import (
    DEFAULT_REPOSITORY_CONTEXT_EXCLUDE_PATTERNS,
    DEFAULT_REPOSITORY_CONTEXT_INCLUDE_PATTERNS,
)
from .repository_context_models import RepositoryContextConfig


def build_repository_context_config(raw_config: dict[str, Any] | None) -> RepositoryContextConfig:
    """Build repository context configuration from task JSON."""

    raw_config = raw_config or {}
    include_patterns = tuple(
        raw_config.get("include_patterns", DEFAULT_REPOSITORY_CONTEXT_INCLUDE_PATTERNS)
    )
    configured_excludes = tuple(raw_config.get("exclude_patterns", []))

    return RepositoryContextConfig(
        enabled=bool(raw_config.get("enabled", False)),
        include_patterns=include_patterns,
        exclude_patterns=DEFAULT_REPOSITORY_CONTEXT_EXCLUDE_PATTERNS + configured_excludes,
        max_files=int(raw_config.get("max_files", 20)),
        max_file_characters=int(raw_config.get("max_file_characters", 4000)),
    )


def disabled_repository_context_config() -> RepositoryContextConfig:
    """Return disabled repository context configuration."""

    return build_repository_context_config({"enabled": False})
