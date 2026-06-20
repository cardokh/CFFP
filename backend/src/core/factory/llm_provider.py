"""LLM provider abstraction for the CCore Automation Factory POC."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol


class LlmProvider(Protocol):
    """Common interface for future LLM providers."""

    def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt."""


@dataclass(frozen=True)
class GeminiProvider:
    """Gemini implementation of the LLM provider interface."""

    model: str

    def generate_text(self, prompt: str) -> str:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Set it as an environment variable before running the factory."
            )

        from google import genai  # Imported here so non-Gemini validation can still run.

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
            "# CCore Automation Factory POC v2\n\n"
            "This mock artifact confirms that the local factory pipeline can read input, "
            "build a prompt, generate text, write an artifact, validate the artifact, "
            "and produce an execution report without calling an external API.\n\n"
            "## Prompt Preview\n\n"
            f"{prompt[:500]}\n"
        )


def create_llm_provider(provider_name: str, gemini_model: str) -> LlmProvider:
    """Create an LLM provider from configuration."""

    normalized_name = provider_name.strip().lower()
    if normalized_name == "gemini":
        return GeminiProvider(model=gemini_model)
    if normalized_name == "mock":
        return MockProvider()
    raise ValueError(f"Unsupported LLM provider: {provider_name}")
