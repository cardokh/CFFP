"""
Automation task registry.

Responsibilities:
- Load registered automation task metadata from JSON configuration.
- Convert registry entries into automation task domain objects.
- Keep v1 script discovery file-based and configuration-driven.
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
        with open(self.registry_path, "r", encoding="utf-8") as registry_file:
            registry_data = json.load(registry_file)

        return [
            self._entry_to_automation_task(entry)
            for entry in registry_data.get("tasks", [])
        ]

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
