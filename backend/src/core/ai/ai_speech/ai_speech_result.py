"""
AI speech result objects.

Responsibilities:
- Represent AI speech generation outcomes.
- Keep service results explicit and transport-independent.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AiSpeechResult:
    success: bool
    provider: Optional[str]
    reason: Optional[str]
    audio: Optional[object]
