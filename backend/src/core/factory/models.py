"""Shared data models for the CCore Automation Factory POC."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FactoryConfig:
    """Factory-level runtime configuration."""

    factory_name: str
    execution_provider: str
    llm_provider: str
    gemini_model: str
    task_definition: Path
    report_dir: Path


@dataclass(frozen=True)
class ArtifactDefinition:
    """Definition of one generated artifact."""

    output_dir: Path
    filename: str
    allowed_extensions: tuple[str, ...]
    max_output_characters: int


@dataclass(frozen=True)
class AutomationTaskDefinition:
    """Configuration-driven automation task definition."""

    task_id: str
    name: str
    description: str
    input_file: Path
    prompt_template: Path
    artifact: ArtifactDefinition
    validations: tuple[str, ...]
