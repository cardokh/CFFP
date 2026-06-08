"""
AI provider utilities.

Responsibilities:
- Centralize AI provider availability checks.
- Keep API key lookup out of feature services.
- Provide reusable AI enablement checks for all AI modules.
"""

from src.core.shared.app_config import (
    get_app_setting,
)
from src.core.shared.app_path_utils import (
    get_path,
)


def get_openai_api_key():
    environment_file_path = get_path(
        "environmentFilePath",
    )

    api_key_environment_variable = get_app_setting(
        "openAiApiKeyEnvironmentVariable",
    )

    if not environment_file_path.exists():
        return None

    with open(environment_file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)

            if key.strip() == api_key_environment_variable:
                return value.strip()

    return None


def is_openai_enabled() -> bool:
    api_key = get_openai_api_key()

    print("OpenAI API Key:", api_key)

    enabled = bool(api_key and api_key.strip())

    print("OpenAI Enabled:", enabled)

    return enabled
