"""
AI speech domain objects.

Responsibilities:
- Define AI speech use-case objects.
- Keep domain/use-case data separate from raw API request dictionaries.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AiSpeechRequest:
    text: str
    speed: float
    voice: str
    tone: str
    accent: str
    intonation: str
