"""Factory LLM provider interface."""

from __future__ import annotations

from typing import Protocol


class ILlmProvider(Protocol):
    """Contract for generating artifacts from compiled prompts."""

    def generate_artifact(self, prompt: str, system_instruction: str | None = None) -> str:
        """Generate one artifact from a prompt and optional system instruction."""
