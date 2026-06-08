"""
API contract utilities.

Responsibilities:
- Convert snake_case DTO dictionaries into camelCase JSON payloads.
- Provide reusable frontend contract helpers across modules.
- Keep backend/database internals snake_case while exposing a stable camelCase API boundary.
"""

from __future__ import annotations


def snake_to_camel_case(name: str) -> str:
    parts = name.split("_")
    if not parts:
        return name

    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def dict_keys_to_camel_case(data: dict) -> dict:
    return {
        snake_to_camel_case(key): _convert_value(value) for key, value in data.items()
    }


def _convert_value(value):
    if isinstance(value, dict):
        return dict_keys_to_camel_case(value)

    if isinstance(value, list):
        return [_convert_value(item) for item in value]

    return value
