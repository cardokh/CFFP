"""
AI speech result factory.

Responsibilities:
- Create AI speech result objects.
- Centralize AI speech outcome construction.
- Keep result-building details out of the service layer.
"""

from src.core.ai.ai_speech.ai_speech_constants import (
    AI_PROVIDER_OPENAI,
    AI_SPEECH_REASON_MISSING_API_KEY,
    AI_SPEECH_REASON_PROVIDER_UNAVAILABLE,
)
from src.core.ai.ai_speech.ai_speech_result import AiSpeechResult


class AiSpeechResultFactory:
    """
    Factory for AI speech generation results.
    """

    def create_missing_api_key_result(self) -> AiSpeechResult:
        return AiSpeechResult(
            success=False,
            provider=None,
            reason=AI_SPEECH_REASON_MISSING_API_KEY,
            audio=None,
        )

    def create_provider_unavailable_result(self) -> AiSpeechResult:
        return AiSpeechResult(
            success=False,
            provider=AI_PROVIDER_OPENAI,
            reason=AI_SPEECH_REASON_PROVIDER_UNAVAILABLE,
            audio=None,
        )

    def create_success_result(
        self,
        audio,
    ) -> AiSpeechResult:
        return AiSpeechResult(
            success=True,
            provider=AI_PROVIDER_OPENAI,
            reason=None,
            audio=audio,
        )
