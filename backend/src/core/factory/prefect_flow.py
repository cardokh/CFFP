"""Prefect flow adapter for the Automation Factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import DEFAULT_FACTORY_NAME
from .dependencies import build_factory_pipeline
from .prefect_compat import flow, get_run_logger, task
from .service import FactoryService


@task(name="Run Automation Factory Service")
def run_factory_service(project_root: Path, config_path: Path | None) -> dict[str, Any]:
    """Run the thin Factory service inside a Prefect task."""

    logger = get_run_logger()
    logger.info("Running Automation Factory for project root: %s", project_root)
    service = FactoryService(pipeline=build_factory_pipeline())
    return service.run_factory(project_root=project_root, config_path=config_path)


@flow(name=DEFAULT_FACTORY_NAME)
def run_factory_pipeline(
    project_root_value: str | None = None,
    config_path_value: str | None = None,
) -> dict[str, Any]:
    """Execute the CCore Automation Factory Prefect flow."""

    project_root = Path(project_root_value).resolve() if project_root_value else Path.cwd().resolve()
    config_path = Path(config_path_value).resolve() if config_path_value else None
    return run_factory_service(project_root, config_path)
