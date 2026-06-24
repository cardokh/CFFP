from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ContextItem:
    """A deterministic context item contributed by a context provider."""

    provider_id: str
    title: str
    source_path: str
    content: str
    metadata: dict


@dataclass(frozen=True)
class ProviderResult:
    """The full result produced by one context provider."""

    provider_id: str
    included_items: list[ContextItem]
    excluded_inputs: list[dict]
    findings: list[dict]
    summary: dict


class ContextProvider(Protocol):
    """Contract for replaceable context providers."""

    provider_id: str

    def collect(self, project_root: Path, config: dict) -> ProviderResult:
        """Collect context from the repository using the supplied provider configuration."""
