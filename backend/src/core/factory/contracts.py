"""Automation Factory contracts.

Factory orchestration depends on these abstractions rather than concrete
implementations. Concrete filesystem, Prefect, Gemini, and validation behavior
is injected through these contracts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from .models import AutomationTaskDefinition, FactoryConfig
from .repository_context_models import RepositoryContextConfig, RepositoryContextPackage


class FactoryConfigRepository(Protocol):
    """Loads Factory and task configuration."""

    def load_config(self, project_root: Path, config_path: Path | None = None) -> FactoryConfig:
        """Load Factory runtime configuration."""

    def load_task_definition(
        self, project_root: Path, task_definition_path: Path
    ) -> AutomationTaskDefinition:
        """Load one automation task definition."""


class RepositoryContextProvider(Protocol):
    """Collects repository context for prompt construction."""

    def collect_context(self, config: RepositoryContextConfig) -> RepositoryContextPackage:
        """Collect a repository context package."""


class RepositoryContextProviderFactory(Protocol):
    """Creates repository context providers."""

    def create_provider(self, project_root: Path) -> RepositoryContextProvider:
        """Create a repository context provider for a project root."""


class LlmProvider(Protocol):
    """Generates text from prompts."""

    def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt."""


class LlmProviderFactory(Protocol):
    """Creates configured LLM providers."""

    def create_provider(self, provider_name: str, model: str) -> LlmProvider:
        """Create an LLM provider by configured provider name."""


class PromptBuilder(Protocol):
    """Builds prompts from task inputs and repository context."""

    def build_prompt(
        self,
        task_definition: AutomationTaskDefinition,
        feature_request: str,
        repository_context: RepositoryContextPackage,
    ) -> str:
        """Build an LLM prompt."""


class ArtifactWriter(Protocol):
    """Writes generated artifacts through controlled filesystem rules."""

    def write_artifact(
        self,
        task_definition: AutomationTaskDefinition,
        generated_text: str,
    ) -> dict[str, object]:
        """Write one generated artifact and return artifact metadata."""


class ValidationProvider(Protocol):
    """Validates generated output and written artifacts."""

    def validate_generated_text(self, generated_text: str, max_characters: int) -> None:
        """Validate generated text."""

    def validate_artifact_path(
        self,
        output_dir: Path,
        artifact_path: Path,
        allowed_extensions: tuple[str, ...],
    ) -> None:
        """Validate artifact path safety."""

    def validate_written_artifact(self, artifact_path: Path) -> dict[str, object]:
        """Validate one written artifact."""


class ReportWriter(Protocol):
    """Writes execution reports."""

    def write_report(
        self,
        report_dir: Path,
        execution_id: str,
        report: dict[str, Any],
    ) -> Path:
        """Write a report and return its path."""


class FactoryPipeline(Protocol):
    """Executes the Factory use case."""

    def execute(
        self,
        project_root: Path,
        config_path: Path | None = None,
    ) -> dict[str, Any]:
        """Execute a Factory pipeline."""
