"""
Automation task registry.

Responsibilities:
- Load registered automation task metadata from JSON configuration.
- Convert registry entries into automation task domain objects.
- Keep script discovery file-based and configuration-driven.
"""

import json

from src.core.automation.automation_task import AutomationTask
from src.core.automation.automation_task_contracts import (
    AUTOMATION_TASK_CATEGORY,
    AUTOMATION_TASK_CONFIG_PATH,
    AUTOMATION_TASK_DESCRIPTION,
    AUTOMATION_TASK_ID,
    AUTOMATION_TASK_NAME,
    AUTOMATION_TASK_SCRIPT_PATH,
    AUTOMATION_TASK_STATUS,
)


class AutomationTaskRegistry:
    def __init__(
        self,
        registry_path,
    ):
        self.registry_path = registry_path

    def find_all_tasks(self) -> list[AutomationTask]:
        registry_data = self._load_registry_data()

        return [
            self._entry_to_automation_task(entry)
            for entry in registry_data.get("tasks", [])
        ]

    def find_task_by_id(self, task_id: str) -> AutomationTask | None:
        normalized_task_id = str(task_id or "").strip()

        for automation_task in self.find_all_tasks():
            if automation_task.task_id == normalized_task_id:
                return automation_task

        return None

    def _load_registry_data(self) -> dict:
        with open(self.registry_path, "r", encoding="utf-8") as registry_file:
            return json.load(registry_file)

    def _entry_to_automation_task(
        self,
        entry: dict,
    ) -> AutomationTask:
        return AutomationTask(
            task_id=entry.get(AUTOMATION_TASK_ID, ""),
            name=entry.get(AUTOMATION_TASK_NAME, ""),
            description=entry.get(AUTOMATION_TASK_DESCRIPTION, ""),
            category=entry.get(AUTOMATION_TASK_CATEGORY, ""),
            status=entry.get(AUTOMATION_TASK_STATUS, ""),
            script_path=entry.get(AUTOMATION_TASK_SCRIPT_PATH, ""),
            config_path=entry.get(AUTOMATION_TASK_CONFIG_PATH, ""),
        )
