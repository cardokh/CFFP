"""
AI speech provider contracts.

Responsibilities:
- Centralize provider-specific transport field names.
- Prevent hardcoded OpenAI request keys across the codebase.
"""

OPENAI_SPEECH_REQUEST_MODEL = "model"

OPENAI_SPEECH_REQUEST_VOICE = "voice"

OPENAI_SPEECH_REQUEST_INPUT = "input"

OPENAI_SPEECH_REQUEST_SPEED = "speed"

OPENAI_SPEECH_REQUEST_INSTRUCTIONS = "instructions"
