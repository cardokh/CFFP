"""Gemini LLM adapter for Factory artifact generation."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"


@dataclass(frozen=True)
class GeminiLlmProvider:
    """Google Gemini implementation of the Factory LLM provider contract."""

    model: str = DEFAULT_GEMINI_MODEL
    api_key_env: str = GEMINI_API_KEY_ENV

    def generate_artifact(self, prompt: str, system_instruction: str | None = None) -> str:
        """Generate an artifact using the Google GenAI SDK."""

        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"{self.api_key_env} is not set.")

        from google import genai

        client = genai.Client(api_key=api_key)
        contents = prompt if not system_instruction else f"{system_instruction}\n\n{prompt}"
        response = client.models.generate_content(model=self.model, contents=contents)
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return str(text)
