"""Pipeline 01 - Context Engineering orchestrator.

The pipeline is intentionally thin: it delegates generic orchestration to the
shared CAutomation pipeline runtime. Business logic lives in individual task
folders under tasks/.

Run from the repository root:

    python CAutomation/ai_engine/pipelines/01_context_engineering/context_engineering_pipeline.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def _configure_project_import_path() -> Path:
    project_root = next(
        (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


_configure_project_import_path()

from CAutomation.ai_engine.runtime.pipeline_runtime import ConfiguredPipelineRuntime  # noqa: E402


class ContextEngineeringPipeline(ConfiguredPipelineRuntime):
    """Orchestrates the configured Context Engineering task sequence."""

    def __init__(self) -> None:
        super().__init__(__file__)


if __name__ == "__main__":
    ContextEngineeringPipeline().run()
