"""Factory dependency composition."""

from __future__ import annotations

from .artifact_writer import FilesystemArtifactWriter
from .config_repository import JsonFactoryConfigRepository
from .context_provider_factory import FilesystemRepositoryContextProviderFactory
from .contracts import FactoryPipeline
from .llm_provider import ConfiguredLlmProviderFactory
from .pipeline import StandardFactoryPipeline
from .prompt_builder import TemplatePromptBuilder
from .reporting import JsonReportWriter
from .validation_provider import StandardValidationProvider


def build_factory_pipeline() -> FactoryPipeline:
    """Compose the default Factory pipeline dependencies."""

    validation_provider = StandardValidationProvider()
    return StandardFactoryPipeline(
        config_repository=JsonFactoryConfigRepository(),
        llm_provider_factory=ConfiguredLlmProviderFactory(),
        prompt_builder=TemplatePromptBuilder(),
        artifact_writer=FilesystemArtifactWriter(validation_provider=validation_provider),
        report_writer=JsonReportWriter(),
        validation_provider=validation_provider,
        repository_context_provider_factory=FilesystemRepositoryContextProviderFactory(),
    )
