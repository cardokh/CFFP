"""
LLA lesson interaction API routes.

Responsibilities:
- Handle runtime lesson interaction endpoints.
- Provide a random learning phrase for simple lesson playback.
- Generate Swedish text-to-speech audio for phrase/pronunciation support.
- Keep lesson runtime/TTS route logic out of app.py.

Architecture:
app.py -> lesson_interaction_routes -> vocabulary/config/TTS support
"""

import json
import random

from urllib.parse import parse_qs, urlparse
from gtts import gTTS

from src.api.api_constants import (
    CONTENT_TYPE_AUDIO_MPEG,
    HTTP_HEADER_CONTENT_LENGTH,
    HTTP_HEADER_CONTENT_TYPE,
    TEXT_ENCODING_UTF8,
    TTS_OUTPUT_FILENAME,
    TTS_SWEDISH_LANGUAGE_CODE,
)
from src.api.route_utils import send_json


def load_vocabulary():
    with open(VOCABULARY_PATH, "r", encoding=TEXT_ENCODING_UTF8) as vocabulary_file:
        return json.load(vocabulary_file)


def get_random_phrase():
    vocabulary = load_vocabulary()
    return random.choice(vocabulary)


def handle_get_lesson_phrase(handler) -> None:
    phrase = get_random_phrase()
    send_json(handler, 200, phrase)


def handle_text_to_speech(handler) -> None:
    query = parse_qs(urlparse(handler.path).query)
    text = query.get("text", [""])[0]

    if not text:
        send_json(handler, 400, {"error": "text required"})
        return

    tts = gTTS(text=text, lang=TTS_SWEDISH_LANGUAGE_CODE)
    tts.save(TTS_OUTPUT_FILENAME)

    with open(TTS_OUTPUT_FILENAME, "rb") as audio_file:
        audio = audio_file.read()

    handler.send_response(200)
    handler.send_header(HTTP_HEADER_CONTENT_TYPE, CONTENT_TYPE_AUDIO_MPEG)
    handler.send_header(HTTP_HEADER_CONTENT_LENGTH, str(len(audio)))
    handler._set_cors_headers()
    handler.end_headers()

    handler.wfile.write(audio)
