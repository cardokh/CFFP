"""Prompt builder implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .models import AutomationTaskDefinition
from .repository_context_models import RepositoryContextPackage


@dataclass(frozen=True)
class TemplatePromptBuilder:
    """Builds prompts from task templates."""

    def build_prompt(
        self,
        task_definition: AutomationTaskDefinition,
        feature_request: str,
        repository_context: RepositoryContextPackage,
    ) -> str:
        template = task_definition.prompt_template.read_text(encoding="utf-8")
        prompt = template.replace("{{FEATURE_REQUEST}}", feature_request.strip())
        return prompt.replace("{{REPOSITORY_CONTEXT}}", repository_context.to_prompt_text())
