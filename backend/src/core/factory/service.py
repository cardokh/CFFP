"""Thin Factory service facade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import FactoryPipeline


@dataclass(frozen=True)
class FactoryService:
    """Thin service layer that delegates to an injected pipeline."""

    pipeline: FactoryPipeline

    def run_factory(
        self,
        project_root: Path,
        config_path: Path | None = None,
    ) -> dict[str, Any]:
        """Run the Factory through the injected pipeline."""

        return self.pipeline.execute(project_root=project_root, config_path=config_path)
