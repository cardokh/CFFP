"""Factory task seed models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FactoryTaskSeed:
    """One seedable Factory task definition."""

    task_id: str
    name: str
    description: str
    task_definition_path: str
    priority: int
    payload: str = '{}'
