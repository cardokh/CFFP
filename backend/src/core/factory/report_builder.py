"""Factory execution report helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import AutomationTaskDefinition, FactoryConfig
from .reporting import utc_now_iso


def create_running_report(execution_id: str, project_root: Path) -> dict[str, Any]:
    """Create the initial report structure."""

    return {
        "execution_id": execution_id,
        "status": "RUNNING",
        "started_at": utc_now_iso(),
        "completed_at": None,
        "project_root": str(project_root),
        "configuration": {},
        "repository_context": {},
        "artifacts": [],
        "validation": [],
        "errors": [],
    }


def configuration_snapshot(
    config: FactoryConfig,
    task_definition: AutomationTaskDefinition,
) -> dict[str, Any]:
    """Create a report snapshot of effective configuration."""

    return {
        "factory_name": config.factory_name,
        "execution_provider": config.execution_provider,
        "llm_provider": config.llm_provider,
        "llm_model": config.llm_model,
        "task_definition_path": str(config.task_definition),
        "task_id": task_definition.task_id,
        "task_name": task_definition.name,
        "input_file": str(task_definition.input_file),
        "prompt_template": str(task_definition.prompt_template),
        "output_dir": str(task_definition.artifact.output_dir),
        "artifact_filename": task_definition.artifact.filename,
        "allowed_output_extensions": list(task_definition.artifact.allowed_extensions),
        "max_output_characters": task_definition.artifact.max_output_characters,
        "configured_validations": list(task_definition.validations),
        "repository_context_enabled": (
            task_definition.repository_context.enabled
            if task_definition.repository_context
            else False
        ),
    }


def passed_validations(task_definition: AutomationTaskDefinition) -> list[dict[str, str]]:
    """Create report entries for configured validations that passed."""

    return [{"name": validation_name, "status": "PASSED"} for validation_name in task_definition.validations]
