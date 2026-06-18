"""
Automation pipeline registry.

Responsibilities:
- Load registered automation pipeline metadata from JSON configuration.
- Convert registry entries into automation pipeline domain objects.
- Keep pipeline discovery file-based and configuration-driven.
- Keep task existence validation out of the first list/details vertical slice.
"""

import json
from pathlib import Path

from src.core.automation.automation_pipeline import (
    AutomationPipeline,
    AutomationPipelineStep,
)
from src.core.automation.automation_pipeline_contracts import (
    AUTOMATION_PIPELINE_CATEGORY,
    AUTOMATION_PIPELINE_DESCRIPTION,
    AUTOMATION_PIPELINE_EXECUTION_MODE,
    AUTOMATION_PIPELINE_FAILURE_STRATEGY,
    AUTOMATION_PIPELINE_ID,
    AUTOMATION_PIPELINE_NAME,
    AUTOMATION_PIPELINE_STATUS,
    AUTOMATION_PIPELINE_STEP_ID,
    AUTOMATION_PIPELINE_STEP_NAME,
    AUTOMATION_PIPELINE_STEP_ORDER,
    AUTOMATION_PIPELINE_STEP_REQUIRED,
    AUTOMATION_PIPELINE_STEP_TASK_ID,
    AUTOMATION_PIPELINE_STEPS,
    AUTOMATION_PIPELINE_VERSION,
)


class AutomationPipelineRegistry:
    def __init__(self, registry_path):
        self.registry_path = Path(registry_path)

    def find_all_pipelines(self) -> list[AutomationPipeline]:
        registry_data = self._load_registry_data()

        return [
            self._entry_to_automation_pipeline(entry)
            for entry in registry_data.get("pipelines", [])
        ]

    def find_pipeline_by_id(self, pipeline_id: str) -> AutomationPipeline | None:
        normalized_pipeline_id = str(pipeline_id or "").strip()

        for automation_pipeline in self.find_all_pipelines():
            if automation_pipeline.pipeline_id == normalized_pipeline_id:
                return automation_pipeline

        return None

    def _load_registry_data(self) -> dict:
        with open(self.registry_path, "r", encoding="utf-8") as registry_file:
            return json.load(registry_file)

    def _entry_to_automation_pipeline(self, entry: dict) -> AutomationPipeline:
        return AutomationPipeline(
            pipeline_id=entry.get(AUTOMATION_PIPELINE_ID, ""),
            name=entry.get(AUTOMATION_PIPELINE_NAME, ""),
            description=entry.get(AUTOMATION_PIPELINE_DESCRIPTION, ""),
            category=entry.get(AUTOMATION_PIPELINE_CATEGORY, ""),
            status=entry.get(AUTOMATION_PIPELINE_STATUS, ""),
            version=entry.get(AUTOMATION_PIPELINE_VERSION, ""),
            execution_mode=entry.get(AUTOMATION_PIPELINE_EXECUTION_MODE, ""),
            failure_strategy=entry.get(AUTOMATION_PIPELINE_FAILURE_STRATEGY, ""),
            steps=[
                self._entry_to_automation_pipeline_step(step_entry)
                for step_entry in entry.get(AUTOMATION_PIPELINE_STEPS, [])
            ],
        )

    def _entry_to_automation_pipeline_step(self, entry: dict) -> AutomationPipelineStep:
        return AutomationPipelineStep(
            step_id=entry.get(AUTOMATION_PIPELINE_STEP_ID, ""),
            order=int(entry.get(AUTOMATION_PIPELINE_STEP_ORDER, 0)),
            name=entry.get(AUTOMATION_PIPELINE_STEP_NAME, ""),
            task_id=entry.get(AUTOMATION_PIPELINE_STEP_TASK_ID, ""),
            required=bool(entry.get(AUTOMATION_PIPELINE_STEP_REQUIRED, False)),
        )
