"""Gemini provider boundary tests."""

from __future__ import annotations

import pytest

from src.infrastructure.ai.gemini.gemini_provider import GeminiLlmProvider


def test_gemini_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY is not set"):
        GeminiLlmProvider().generate_artifact("prompt")
