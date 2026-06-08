"""
AI speech messages.

Responsibilities:
- Centralize user-facing and API-facing AI speech messages.
- Avoid hardcoded response/error text in routes and services.
"""

AI_SPEECH_TEXT_REQUIRED = "Text is required."

AI_SPEECH_TEXT_TOO_LONG = "Text is too long."

AI_SPEECH_INVALID_SPEED = "Speech speed must be between 0.25 and 4.0."

AI_SPEECH_INVALID_VOICE = "Unsupported speech voice."

AI_SPEECH_GENERATION_FAILED = "AI speech generation failed."

AI_SPEECH_GENERATED_SUCCESSFULLY = "AI speech generated successfully."

AI_SPEECH_MISSING_API_KEY = (
    "AI speech could not be generated because the OpenAI API key is missing."
)

AI_SPEECH_PROVIDER_UNAVAILABLE = (
    "AI speech could not be generated because the OpenAI provider is unavailable."
)
