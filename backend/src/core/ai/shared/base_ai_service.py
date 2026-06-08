"""
Base AI service.

Responsibilities:
- Centralize shared AI provider configuration.
- Avoid duplicated API key lookup logic across AI services.
- Provide reusable AI enablement state for AI modules.
"""

from src.core.ai.shared.ai_provider_utils import (
    get_openai_api_key,
    is_openai_enabled,
)


class BaseAiService:
    """
    Base class for AI services.
    """

    def __init__(self):
        self._is_openai_enabled = is_openai_enabled()

        self._openai_api_key = get_openai_api_key()

    @property
    def is_openai_enabled(self) -> bool:
        return self._is_openai_enabled

    @property
    def openai_api_key(self):
        return self._openai_api_key
