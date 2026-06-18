"""
Automation task service.

Responsibilities:
- Coordinate automation task discovery use cases.
- Load inspect-only task configuration data for visualization.
- Keep API handlers separate from registry-loading details.
- Keep task listing and task detail lookup independent from database storage.
"""


class AutomationTaskService:
    def __init__(
        self,
        automation_task_registry,
        automation_task_validation_service=None,
        automation_task_execution_service=None,
    ):
        self.automation_task_registry = automation_task_registry
        self.automation_task_validation_service = automation_task_validation_service
        self.automation_task_execution_service = automation_task_execution_service

    def get_all_tasks(self):
        return self.automation_task_registry.find_all_tasks()

    def get_task_by_id(self, task_id: str):
        return self.automation_task_registry.find_task_by_id(
            task_id=task_id,
        )

    def get_task_configuration_by_id(self, task_id: str):
        automation_task = self.get_task_by_id(
            task_id=task_id,
        )

        if automation_task is None:
            return None

        configuration = self.automation_task_registry.load_task_configuration(
            automation_task,
        )

        return {
            "task": automation_task,
            "configuration": configuration,
        }


    def validate_task_by_id(self, task_id: str):
        automation_task = self.get_task_by_id(
            task_id=task_id,
        )

        if automation_task is None:
            return None

        if self.automation_task_validation_service is None:
            raise ValueError("Automation task validation service is not configured.")

        return {
            "task": automation_task,
            "validation": self.automation_task_validation_service.validate_task(
                automation_task,
            ),
        }



    def list_task_executions_by_id(self, task_id: str):
        automation_task = self.get_task_by_id(
            task_id=task_id,
        )

        if automation_task is None:
            return None

        if self.automation_task_execution_service is None:
            raise ValueError("Automation task execution service is not configured.")

        return {
            "task": automation_task,
            "executions": self.automation_task_execution_service.list_task_execution_reports(
                task_id=task_id,
            ),
        }


    def get_task_execution_report_by_id(
        self,
        task_id: str,
        execution_id: str,
    ):
        automation_task = self.get_task_by_id(
            task_id=task_id,
        )

        if automation_task is None:
            return None

        if self.automation_task_execution_service is None:
            raise ValueError("Automation task execution service is not configured.")

        execution_report = self.automation_task_execution_service.get_task_execution_report(
            task_id=task_id,
            execution_id=execution_id,
        )

        if execution_report is None:
            return None

        return {
            "task": automation_task,
            "execution_report": execution_report,
        }

    def execute_task_by_id(self, task_id: str):
        automation_task = self.get_task_by_id(
            task_id=task_id,
        )

        if automation_task is None:
            return None

        if self.automation_task_execution_service is None:
            raise ValueError("Automation task execution service is not configured.")

        return {
            "task": automation_task,
            "execution": self.automation_task_execution_service.execute_task(
                automation_task,
            ),
        }
