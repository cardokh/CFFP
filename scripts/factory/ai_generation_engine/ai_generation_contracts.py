from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class PromptMetadata:
    """Metadata for the exact prompt sent to a replaceable LLM provider."""

    prompt_id: str
    source_path: str
    source_sha256: str
    prompt_sha256: str
    character_count: int
    line_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LlmGenerationOptions:
    """Provider-independent generation options loaded from configuration."""

    model: str | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "LlmGenerationOptions":
        return cls(
            model=config.get("model"),
            temperature=config.get("temperature"),
            max_output_tokens=config.get("maxOutputTokens"),
            extra=dict(config.get("extra", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "maxOutputTokens": self.max_output_tokens,
            "extra": self.extra,
        }


@dataclass(frozen=True)
class LlmGenerationResult:
    """Provider-independent result returned by any LLM provider implementation."""

    provider_id: str
    model_metadata: dict[str, Any]
    response_text: str
    finish_reason: str = "unknown"
    usage_metadata: dict[str, Any] = field(default_factory=dict)

    def to_report_dict(self, response_sha256: str) -> dict[str, Any]:
        return {
            "providerId": self.provider_id,
            "modelMetadata": self.model_metadata,
            "responseSha256": response_sha256,
            "finishReason": self.finish_reason,
            "usageMetadata": self.usage_metadata,
        }


class LlmProvider(Protocol):
    """Replaceable LLM provider boundary for the AI Generation Engine."""

    provider_id: str

    def generate(
        self,
        *,
        prompt: str,
        options: LlmGenerationOptions,
    ) -> LlmGenerationResult:
        """Generate raw provider output from a prompt and provider-neutral options."""
