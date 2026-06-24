from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PromptMetadata:
    """Metadata describing the prompt sent to the configured LLM provider."""

    prompt_id: str
    source_path: str
    source_sha256: str
    prompt_sha256: str
    character_count: int
    line_count: int


@dataclass(frozen=True)
class LlmGenerationResponse:
    """Provider-independent LLM generation result."""

    provider_id: str
    model_metadata: dict
    response_text: str
    response_sha256: str
    finish_reason: str
    usage_metadata: dict


class LlmProvider(Protocol):
    """Replaceable contract for AI generation providers."""

    provider_id: str

    def generate(
        self,
        *,
        prompt: str,
        prompt_metadata: PromptMetadata,
        provider_config: dict,
    ) -> LlmGenerationResponse:
        """Generate provider output from the supplied prompt."""
