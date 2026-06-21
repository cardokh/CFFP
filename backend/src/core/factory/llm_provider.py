"""Backward-compatible local LLM provider factory.

External SDK-backed LLM implementations live in infrastructure adapters.
"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import DEFAULT_MOCK_LLM_PROVIDER
from .contracts import LlmProvider


@dataclass(frozen=True)
class MockProvider:
    """Local provider for offline validation and smoke testing."""

    def generate_text(self, prompt: str) -> str:
        return (
            "# CCore Automation Factory\n\n"
            "This mock artifact confirms that the local factory pipeline can read input, "
            "build a prompt, generate text, write an artifact, validate the artifact, "
            "and produce an execution report without calling an external API.\n\n"
            "## Prompt Preview\n\n"
            f"{prompt[:500]}\n"
        )


@dataclass(frozen=True)
class ConfiguredLlmProviderFactory:
    """Creates configured local LLM providers."""

    def create_provider(self, provider_name: str, model: str) -> LlmProvider:
        normalized_name = provider_name.strip().lower()
        if normalized_name == DEFAULT_MOCK_LLM_PROVIDER:
            return MockProvider()
        raise ValueError(
            "SDK-backed LLM providers are infrastructure adapters. "
            f"Unsupported core provider: {provider_name}"
        )


def create_llm_provider(provider_name: str, gemini_model: str) -> LlmProvider:
    """Backward-compatible LLM provider factory function."""

    return ConfiguredLlmProviderFactory().create_provider(provider_name, gemini_model)
