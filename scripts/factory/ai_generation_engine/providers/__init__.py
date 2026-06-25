"""
Provider implementations for the CFFP AI Generation Engine.

This package contains optional vendor adapters. Core factory orchestration,
context compilation, and validation/apply logic must not import vendor SDKs.
"""

from scripts.factory.ai_generation_engine.providers.gemini_provider import GeminiProvider

__all__ = ["GeminiProvider"]
