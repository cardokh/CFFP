"""
Automation pipeline service.

Responsibilities:
- Coordinate automation pipeline discovery use cases.
- Keep API handlers separate from registry-loading details.
- Keep pipeline listing and detail lookup independent from database storage.
- Keep execution orchestration out of the first list/details vertical slice.
"""


class AutomationPipelineService:
    def __init__(self, automation_pipeline_registry):
        self.automation_pipeline_registry = automation_pipeline_registry

    def get_all_pipelines(self):
        return self.automation_pipeline_registry.find_all_pipelines()

    def get_pipeline_by_id(self, pipeline_id: str):
        return self.automation_pipeline_registry.find_pipeline_by_id(
            pipeline_id=pipeline_id,
        )
