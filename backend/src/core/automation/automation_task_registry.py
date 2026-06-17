"""
Automation task registry.

Responsibilities:
- Load registered automation task metadata from JSON configuration.
- Convert registry entries into automation task domain objects.
- Load task configuration JSON for inspect-only visualization.
- Keep script discovery file-based and configuration-driven.
"""

import json
from pathlib import Path

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
        project_root=None,
    ):
        self.registry_path = Path(registry_path)
        self.project_root = Path(project_root).resolve() if project_root else None

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

    def load_task_configuration(self, automation_task: AutomationTask) -> dict:
        config_path = self._resolve_project_relative_path(
            automation_task.config_path,
        )

        with open(config_path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)

    def _load_registry_data(self) -> dict:
        with open(self.registry_path, "r", encoding="utf-8") as registry_file:
            return json.load(registry_file)

    def _resolve_project_relative_path(self, relative_path: str) -> Path:
        if self.project_root is None:
            raise ValueError("Project root is required to resolve task configuration paths.")

        normalized_relative_path = str(relative_path or "").strip()

        candidate_path = (self.project_root / normalized_relative_path).resolve()

        if not self._is_within_project_root(candidate_path):
            raise ValueError("Task configuration path must stay inside the project root.")

        return candidate_path

    def _is_within_project_root(self, candidate_path: Path) -> bool:
        try:
            candidate_path.relative_to(self.project_root)
            return True
        except ValueError:
            return False

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
