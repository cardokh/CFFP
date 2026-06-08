"""
AI speech constants.

Responsibilities:
- Centralize AI speech configuration constants.
- Avoid hardcoded model, voice, speed, tone, accent, and intonation values.
"""

AI_SPEECH_MODEL = "gpt-4o-mini-tts"

AI_SPEECH_DEFAULT_VOICE = "alloy"

AI_SPEECH_DEFAULT_SPEED = 1.0
AI_SPEECH_SLOW_SPEED = 0.65

AI_SPEECH_MIN_SPEED = 0.25
AI_SPEECH_MAX_SPEED = 4.0

AI_SPEECH_DEFAULT_TONE = "clear and encouraging"
AI_SPEECH_DEFAULT_ACCENT = "neutral Swedish"
AI_SPEECH_DEFAULT_INTONATION = "calm and natural"

AI_SPEECH_AUDIO_FORMAT_MP3 = "mp3"
AI_SPEECH_CONTENT_TYPE_MP3 = "audio/mpeg"

AI_PROVIDER_OPENAI = "openai"

AI_SPEECH_REASON_MISSING_API_KEY = "missingApiKey"
AI_SPEECH_REASON_PROVIDER_UNAVAILABLE = "providerUnavailable"
