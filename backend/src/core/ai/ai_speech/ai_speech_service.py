"""
AI speech service.

Responsibilities:
- Orchestrate AI speech generation.
- Reuse shared AI provider configuration from BaseAiService.
- Delegate result construction to AiSpeechResultFactory.
- Keep provider-specific request construction out of the service layer.
"""

from openai import OpenAI

from src.core.ai.shared.base_ai_service import BaseAiService


class AiSpeechService(BaseAiService):
    """
    Service for AI speech generation.
    """

    def __init__(
        self,
        ai_speech_provider_mapper,
        ai_speech_result_factory,
    ):
        super().__init__()

        self._ai_speech_provider_mapper = ai_speech_provider_mapper
        self._ai_speech_result_factory = ai_speech_result_factory

    def generate_speech(
        self,
        ai_speech_request,
    ):
        if not self.is_openai_enabled:
            return self._ai_speech_result_factory.create_missing_api_key_result()

        try:
            openai_client = OpenAI(
                api_key=self.openai_api_key,
            )

            openai_request = self._ai_speech_provider_mapper.to_openai_speech_request(
                ai_speech_request,
            )

            response = openai_client.audio.speech.create(**openai_request)

            return self._ai_speech_result_factory.create_success_result(
                response,
            )

        except Exception:
            return self._ai_speech_result_factory.create_provider_unavailable_result()
