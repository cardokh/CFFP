"""
AI speech routes.

Responsibilities:
- Handle AI speech HTTP requests.
- Convert transport requests into domain requests.
- Delegate validation and speech generation.
- Return HTTP responses.
"""

from src.api.route_utils import read_json_body, send_json
from src.core.ai.ai_speech.ai_speech_contracts import (
    AI_SPEECH_RESPONSE_MESSAGE,
)
from src.core.ai.ai_speech.ai_speech_mapper import (
    ai_speech_result_to_response,
    request_to_ai_speech_request,
)
from src.core.ai.ai_speech.ai_speech_messages import (
    AI_SPEECH_GENERATION_FAILED,
)


def handle_generate_ai_speech(
    handler,
    ai_speech_service,
    ai_speech_validator,
):
    try:
        request_data = read_json_body(handler)

        ai_speech_request = request_to_ai_speech_request(
            request_data,
        )

        ai_speech_validator.validate(
            ai_speech_request,
        )

        ai_speech_result = ai_speech_service.generate_speech(
            ai_speech_request,
        )

        send_json(
            handler,
            200,
            ai_speech_result_to_response(
                ai_speech_result,
            ),
        )

    except ValueError as error:
        send_json(
            handler,
            400,
            {
                AI_SPEECH_RESPONSE_MESSAGE: str(error),
            },
        )

    except Exception:
        send_json(
            handler,
            500,
            {
                AI_SPEECH_RESPONSE_MESSAGE: AI_SPEECH_GENERATION_FAILED,
            },
        )
