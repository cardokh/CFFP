"""Configuration loading public API."""

from __future__ import annotations

from pathlib import Path

from .config_repository import JsonFactoryConfigRepository
from .models import AutomationTaskDefinition, FactoryConfig


def load_config(project_root: Path, config_path: Path | None = None) -> FactoryConfig:
    """Load Factory configuration using the default JSON repository."""

    return JsonFactoryConfigRepository().load_config(project_root, config_path)


def load_task_definition(project_root: Path, task_definition_path: Path) -> AutomationTaskDefinition:
    """Load one task definition using the default JSON repository."""

    return JsonFactoryConfigRepository().load_task_definition(project_root, task_definition_path)
