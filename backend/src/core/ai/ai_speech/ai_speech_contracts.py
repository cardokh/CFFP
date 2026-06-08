"""
AI speech contracts.

Responsibilities:
- Define API transport contracts for AI speech requests and responses.
- Keep transport-layer field names centralized.
"""

AI_SPEECH_REQUEST_TEXT = "text"
AI_SPEECH_REQUEST_SPEED = "speed"
AI_SPEECH_REQUEST_VOICE = "voice"
AI_SPEECH_REQUEST_TONE = "tone"
AI_SPEECH_REQUEST_ACCENT = "accent"
AI_SPEECH_REQUEST_INTONATION = "intonation"

AI_SPEECH_RESPONSE_SUCCESS = "success"
AI_SPEECH_RESPONSE_PROVIDER = "provider"
AI_SPEECH_RESPONSE_REASON = "reason"
AI_SPEECH_RESPONSE_MESSAGE = "message"
AI_SPEECH_RESPONSE_AUDIO = "audio"
