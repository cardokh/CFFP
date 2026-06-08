"""
AI speech validator.

Responsibilities:
- Validate AI speech domain requests.
- Keep validation logic out of routes and services.
"""

from src.core.ai.ai_speech.ai_speech_messages import (
    AI_SPEECH_INVALID_SPEED,
    AI_SPEECH_TEXT_REQUIRED,
    AI_SPEECH_TEXT_TOO_LONG,
)


class AiSpeechValidator:
    """
    Validates AI speech requests.
    """

    MAX_TEXT_LENGTH = 4000

    MIN_SPEED = 0.25

    MAX_SPEED = 4.0

    def validate(
        self,
        ai_speech_request,
    ) -> None:
        self._validate_text(
            ai_speech_request.text,
        )

        self._validate_speed(
            ai_speech_request.speed,
        )

    def _validate_text(
        self,
        text: str,
    ) -> None:
        if not text or not text.strip():
            raise ValueError(
                AI_SPEECH_TEXT_REQUIRED,
            )

        if len(text) > self.MAX_TEXT_LENGTH:
            raise ValueError(
                AI_SPEECH_TEXT_TOO_LONG,
            )

    def _validate_speed(
        self,
        speed: float,
    ) -> None:
        if speed < self.MIN_SPEED or speed > self.MAX_SPEED:
            raise ValueError(
                AI_SPEECH_INVALID_SPEED,
            )
