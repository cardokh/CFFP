"""
AI speech provider mapper.

Responsibilities:
- Convert AI speech domain requests into provider-specific request values.
- Keep OpenAI-specific instruction-building out of the service layer.
"""

from src.core.ai.ai_speech.ai_speech_constants import (
    AI_SPEECH_MODEL,
)
from src.core.ai.ai_speech.ai_speech_provider_contracts import (
    OPENAI_SPEECH_REQUEST_INPUT,
    OPENAI_SPEECH_REQUEST_INSTRUCTIONS,
    OPENAI_SPEECH_REQUEST_MODEL,
    OPENAI_SPEECH_REQUEST_SPEED,
    OPENAI_SPEECH_REQUEST_VOICE,
)


class AiSpeechProviderMapper:
    """
    Maps AI speech domain requests to OpenAI speech request arguments.
    """

    def to_openai_speech_request(
        self,
        ai_speech_request,
    ) -> dict:
        return {
            OPENAI_SPEECH_REQUEST_MODEL: AI_SPEECH_MODEL,
            OPENAI_SPEECH_REQUEST_VOICE: ai_speech_request.voice,
            OPENAI_SPEECH_REQUEST_INPUT: ai_speech_request.text,
            OPENAI_SPEECH_REQUEST_SPEED: ai_speech_request.speed,
            OPENAI_SPEECH_REQUEST_INSTRUCTIONS: (
                self._build_instructions(
                    ai_speech_request,
                )
            ),
        }

    def _build_instructions(
        self,
        ai_speech_request,
    ) -> str:
        return (
            f"Tone: {ai_speech_request.tone}. "
            f"Accent: {ai_speech_request.accent}. "
            f"Intonation: {ai_speech_request.intonation}."
        )
