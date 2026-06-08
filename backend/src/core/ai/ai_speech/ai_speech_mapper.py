"""
AI speech mapper.

Responsibilities:
- Convert raw API request dictionaries into AI speech domain objects.
- Convert AI speech result objects into API response dictionaries.
- Keep transport field names out of routes and services.
"""

from src.core.ai.ai_speech.ai_speech import AiSpeechRequest
from src.core.ai.ai_speech.ai_speech_constants import (
    AI_SPEECH_DEFAULT_ACCENT,
    AI_SPEECH_DEFAULT_INTONATION,
    AI_SPEECH_DEFAULT_SPEED,
    AI_SPEECH_DEFAULT_TONE,
    AI_SPEECH_DEFAULT_VOICE,
    AI_SPEECH_REASON_MISSING_API_KEY,
    AI_SPEECH_REASON_PROVIDER_UNAVAILABLE,
)
from src.core.ai.ai_speech.ai_speech_contracts import (
    AI_SPEECH_REQUEST_ACCENT,
    AI_SPEECH_REQUEST_INTONATION,
    AI_SPEECH_REQUEST_SPEED,
    AI_SPEECH_REQUEST_TEXT,
    AI_SPEECH_REQUEST_TONE,
    AI_SPEECH_REQUEST_VOICE,
    AI_SPEECH_RESPONSE_AUDIO,
    AI_SPEECH_RESPONSE_MESSAGE,
    AI_SPEECH_RESPONSE_PROVIDER,
    AI_SPEECH_RESPONSE_REASON,
    AI_SPEECH_RESPONSE_SUCCESS,
)
from src.core.ai.ai_speech.ai_speech_messages import (
    AI_SPEECH_GENERATED_SUCCESSFULLY,
    AI_SPEECH_MISSING_API_KEY,
    AI_SPEECH_PROVIDER_UNAVAILABLE,
)


def request_to_ai_speech_request(request_data: dict) -> AiSpeechRequest:
    return AiSpeechRequest(
        text=request_data.get(AI_SPEECH_REQUEST_TEXT, ""),
        speed=request_data.get(
            AI_SPEECH_REQUEST_SPEED,
            AI_SPEECH_DEFAULT_SPEED,
        ),
        voice=request_data.get(
            AI_SPEECH_REQUEST_VOICE,
            AI_SPEECH_DEFAULT_VOICE,
        ),
        tone=request_data.get(
            AI_SPEECH_REQUEST_TONE,
            AI_SPEECH_DEFAULT_TONE,
        ),
        accent=request_data.get(
            AI_SPEECH_REQUEST_ACCENT,
            AI_SPEECH_DEFAULT_ACCENT,
        ),
        intonation=request_data.get(
            AI_SPEECH_REQUEST_INTONATION,
            AI_SPEECH_DEFAULT_INTONATION,
        ),
    )


def ai_speech_result_to_response(
    ai_speech_result,
) -> dict:
    return {
        AI_SPEECH_RESPONSE_SUCCESS: ai_speech_result.success,
        AI_SPEECH_RESPONSE_PROVIDER: ai_speech_result.provider,
        AI_SPEECH_RESPONSE_REASON: ai_speech_result.reason,
        AI_SPEECH_RESPONSE_MESSAGE: _message_for_result(
            ai_speech_result,
        ),
        AI_SPEECH_RESPONSE_AUDIO: ai_speech_result.audio,
    }


def _message_for_result(
    ai_speech_result,
) -> str:
    if ai_speech_result.success:
        return AI_SPEECH_GENERATED_SUCCESSFULLY

    if ai_speech_result.reason == AI_SPEECH_REASON_MISSING_API_KEY:
        return AI_SPEECH_MISSING_API_KEY

    if ai_speech_result.reason == AI_SPEECH_REASON_PROVIDER_UNAVAILABLE:
        return AI_SPEECH_PROVIDER_UNAVAILABLE

    return AI_SPEECH_PROVIDER_UNAVAILABLE
