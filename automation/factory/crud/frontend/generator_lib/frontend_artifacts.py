"""Frontend CRUD generation result models."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrontendGenerationResult:
    generated_entity: str
    written_files: list[str]
    unchanged_files: list[str]
    dashboard_updated: bool
    api_endpoints_updated: bool
