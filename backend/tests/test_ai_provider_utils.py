import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"

sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

from src.core.ai.shared.ai_provider_utils import (
    is_openai_enabled,
)


def main():
    print(is_openai_enabled())


if __name__ == "__main__":
    main()
