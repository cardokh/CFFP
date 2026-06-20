"""Filesystem Factory configuration repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import DEFAULT_FACTORY_CONFIG_PATH
from .models import ArtifactDefinition, AutomationTaskDefinition, FactoryConfig
from .repository_context_config import build_repository_context_config


class JsonFactoryConfigRepository:
    """Loads Factory configuration from JSON files."""

    def load_config(self, project_root: Path, config_path: Path | None = None) -> FactoryConfig:
        """Load and normalize Factory configuration."""

        resolved_config_path = config_path or project_root / DEFAULT_FACTORY_CONFIG_PATH
        raw_config = self._read_json(resolved_config_path)

        return FactoryConfig(
            factory_name=str(raw_config["factory_name"]),
            execution_provider=str(raw_config["execution_provider"]).strip().lower(),
            llm_provider=str(raw_config["llm_provider"]).strip().lower(),
            llm_model=str(raw_config.get("llm_model", raw_config.get("gemini_model", ""))),
            task_definition=project_root / raw_config["task_definition"],
            report_dir=project_root / raw_config["report_dir"],
        )

    def load_task_definition(
        self, project_root: Path, task_definition_path: Path
    ) -> AutomationTaskDefinition:
        """Load one configuration-driven automation task definition."""

        raw_task = self._read_json(task_definition_path)
        raw_artifact = raw_task["artifact"]

        artifact = ArtifactDefinition(
            output_dir=project_root / raw_artifact["output_dir"],
            filename=str(raw_artifact["filename"]),
            allowed_extensions=tuple(raw_artifact["allowed_extensions"]),
            max_output_characters=int(raw_artifact["max_output_characters"]),
        )

        return AutomationTaskDefinition(
            task_id=str(raw_task["task_id"]),
            name=str(raw_task["name"]),
            description=str(raw_task.get("description", "")),
            input_file=project_root / raw_task["input_file"],
            prompt_template=project_root / raw_task["prompt_template"],
            artifact=artifact,
            validations=tuple(raw_task.get("validations", [])),
            repository_context=build_repository_context_config(raw_task.get("repository_context")),
        )

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)
