"""
Automation pipeline API contracts.

Responsibilities:
- Centralize transport field names for automation pipeline responses.
- Keep response dictionaries consistent across routes, mappers, and tests.
- Keep orchestration contract fields separate from automation task contracts.
"""

AUTOMATION_PIPELINE_RESPONSE_PIPELINE = "pipeline"
AUTOMATION_PIPELINE_RESPONSE_PIPELINES = "pipelines"

AUTOMATION_PIPELINE_ID = "id"
AUTOMATION_PIPELINE_NAME = "name"
AUTOMATION_PIPELINE_DESCRIPTION = "description"
AUTOMATION_PIPELINE_CATEGORY = "category"
AUTOMATION_PIPELINE_STATUS = "status"
AUTOMATION_PIPELINE_VERSION = "version"
AUTOMATION_PIPELINE_EXECUTION_MODE = "execution_mode"
AUTOMATION_PIPELINE_FAILURE_STRATEGY = "failure_strategy"
AUTOMATION_PIPELINE_STEPS = "steps"

AUTOMATION_PIPELINE_STEP_ID = "id"
AUTOMATION_PIPELINE_STEP_ORDER = "order"
AUTOMATION_PIPELINE_STEP_NAME = "name"
AUTOMATION_PIPELINE_STEP_TASK_ID = "task_id"
AUTOMATION_PIPELINE_STEP_REQUIRED = "required"
