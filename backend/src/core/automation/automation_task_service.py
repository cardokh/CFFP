"""
Automation task service.

Responsibilities:
- Coordinate automation task discovery use cases.
- Keep API handlers separate from registry-loading details.
- Keep task listing and task detail lookup independent from database storage.
"""


class AutomationTaskService:
    def __init__(
        self,
        automation_task_registry,
    ):
        self.automation_task_registry = automation_task_registry

    def get_all_tasks(self):
        return self.automation_task_registry.find_all_tasks()

    def get_task_by_id(self, task_id: str):
        return self.automation_task_registry.find_task_by_id(
            task_id=task_id,
        )
