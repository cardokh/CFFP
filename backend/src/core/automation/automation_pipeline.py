"""
Automation pipeline domain objects.

Responsibilities:
- Represent registered automation pipelines as domain objects.
- Keep pipeline orchestration metadata separate from raw registry JSON.
- Keep pipeline steps as task references only; tasks remain responsible for work.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationPipelineStep:
    step_id: str
    order: int
    name: str
    task_id: str
    required: bool


@dataclass(frozen=True)
class AutomationPipeline:
    pipeline_id: str
    name: str
    description: str
    category: str
    status: str
    version: str
    execution_mode: str
    failure_strategy: str
    steps: list[AutomationPipelineStep]
