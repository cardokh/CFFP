"""AI provider composition helpers."""

from __future__ import annotations

from src.core.factory.interfaces.llm_provider import ILlmProvider
from src.infrastructure.ai.gemini.gemini_provider import DEFAULT_GEMINI_MODEL, GeminiLlmProvider
from src.infrastructure.ai.mock.mock_llm_provider import MockLlmProvider

DEFAULT_LLM_PROVIDER = "mock"
GEMINI_PROVIDER = "gemini"
MOCK_PROVIDER = "mock"


def build_llm_provider(provider_name: str | None = None, model: str | None = None) -> ILlmProvider:
    """Build an LLM provider adapter by name."""

    normalized_provider = (provider_name or DEFAULT_LLM_PROVIDER).strip().lower()
    if normalized_provider == MOCK_PROVIDER:
        return MockLlmProvider()
    if normalized_provider == GEMINI_PROVIDER:
        return GeminiLlmProvider(model=model or DEFAULT_GEMINI_MODEL)
    raise ValueError(f"Unsupported LLM provider: {provider_name}")
