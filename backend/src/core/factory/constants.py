"""Automation Factory constants."""

from __future__ import annotations

DEFAULT_FACTORY_CONFIG_PATH = "backend/src/core/factory/config/factory_config.json"
DEFAULT_FACTORY_TASK_SEED_PATH = "backend/src/core/factory/config/factory_task_seed.json"
DEFAULT_FACTORY_NAME = "CCore Automation Factory"
DEFAULT_EXECUTION_PROVIDER = "prefect"
DEFAULT_LLM_PROVIDER = "gemini"
DEFAULT_MOCK_LLM_PROVIDER = "mock"

DEFAULT_REPOSITORY_CONTEXT_INCLUDE_PATTERNS: tuple[str, ...] = (
    "**/*.py",
    "**/*.json",
    "**/*.md",
)

DEFAULT_REPOSITORY_CONTEXT_EXCLUDE_PATTERNS: tuple[str, ...] = (
    ".git/**",
    ".venv/**",
    "**/__pycache__/**",
    "**/.pytest_cache/**",
    "**/*.pyc",
    "runtime/**",
    "backend/src/core/factory/reports/**",
    "backend/src/core/factory/output/**",
    "scripts/tasks/output/**",
    ".env",
    "**/.env",
    "**/*.pem",
    "**/*.key",
    "**/*secret*",
    "**/*credential*",
)

TEXT_FILE_EXTENSIONS: tuple[str, ...] = (
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".sql",
    ".txt",
    ".yaml",
    ".yml",
)
