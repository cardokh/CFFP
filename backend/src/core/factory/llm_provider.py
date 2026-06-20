"""LLM provider implementations and factory."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .constants import DEFAULT_LLM_PROVIDER, DEFAULT_MOCK_LLM_PROVIDER
from .contracts import LlmProvider


@dataclass(frozen=True)
class GeminiProvider:
    """Gemini implementation of the LLM provider contract."""

    model: str

    def generate_text(self, prompt: str) -> str:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Set it as an environment variable before running the factory."
            )

        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=self.model, contents=prompt)
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return str(text)


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
    """Creates configured LLM providers."""

    def create_provider(self, provider_name: str, model: str) -> LlmProvider:
        normalized_name = provider_name.strip().lower()
        if normalized_name == DEFAULT_LLM_PROVIDER:
            return GeminiProvider(model=model)
        if normalized_name == DEFAULT_MOCK_LLM_PROVIDER:
            return MockProvider()
        raise ValueError(f"Unsupported LLM provider: {provider_name}")


def create_llm_provider(provider_name: str, gemini_model: str) -> LlmProvider:
    """Backward-compatible LLM provider factory function."""

    return ConfiguredLlmProviderFactory().create_provider(provider_name, gemini_model)
