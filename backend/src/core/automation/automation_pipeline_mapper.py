"""
Automation pipeline mapper.

Responsibilities:
- Convert automation pipeline domain objects into API response dictionaries.
- Keep transport field names out of routes and services.
- Preserve pipeline step task references without validating task existence yet.
"""

from src.core.automation.automation_pipeline_contracts import (
    AUTOMATION_PIPELINE_CATEGORY,
    AUTOMATION_PIPELINE_DESCRIPTION,
    AUTOMATION_PIPELINE_EXECUTION_MODE,
    AUTOMATION_PIPELINE_FAILURE_STRATEGY,
    AUTOMATION_PIPELINE_ID,
    AUTOMATION_PIPELINE_NAME,
    AUTOMATION_PIPELINE_RESPONSE_PIPELINE,
    AUTOMATION_PIPELINE_RESPONSE_PIPELINES,
    AUTOMATION_PIPELINE_STATUS,
    AUTOMATION_PIPELINE_STEP_ID,
    AUTOMATION_PIPELINE_STEP_NAME,
    AUTOMATION_PIPELINE_STEP_ORDER,
    AUTOMATION_PIPELINE_STEP_REQUIRED,
    AUTOMATION_PIPELINE_STEP_TASK_ID,
    AUTOMATION_PIPELINE_STEPS,
    AUTOMATION_PIPELINE_VERSION,
)


def automation_pipeline_step_to_response(automation_pipeline_step) -> dict:
    return {
        AUTOMATION_PIPELINE_STEP_ID: automation_pipeline_step.step_id,
        AUTOMATION_PIPELINE_STEP_ORDER: automation_pipeline_step.order,
        AUTOMATION_PIPELINE_STEP_NAME: automation_pipeline_step.name,
        AUTOMATION_PIPELINE_STEP_TASK_ID: automation_pipeline_step.task_id,
        AUTOMATION_PIPELINE_STEP_REQUIRED: automation_pipeline_step.required,
    }


def automation_pipeline_to_response(automation_pipeline) -> dict:
    return {
        AUTOMATION_PIPELINE_ID: automation_pipeline.pipeline_id,
        AUTOMATION_PIPELINE_NAME: automation_pipeline.name,
        AUTOMATION_PIPELINE_DESCRIPTION: automation_pipeline.description,
        AUTOMATION_PIPELINE_CATEGORY: automation_pipeline.category,
        AUTOMATION_PIPELINE_STATUS: automation_pipeline.status,
        AUTOMATION_PIPELINE_VERSION: automation_pipeline.version,
        AUTOMATION_PIPELINE_EXECUTION_MODE: automation_pipeline.execution_mode,
        AUTOMATION_PIPELINE_FAILURE_STRATEGY: automation_pipeline.failure_strategy,
        AUTOMATION_PIPELINE_STEPS: [
            automation_pipeline_step_to_response(automation_pipeline_step)
            for automation_pipeline_step in automation_pipeline.steps
        ],
    }


def automation_pipeline_detail_to_response(automation_pipeline) -> dict:
    return {
        AUTOMATION_PIPELINE_RESPONSE_PIPELINE: automation_pipeline_to_response(
            automation_pipeline,
        ),
    }


def automation_pipelines_to_response(automation_pipelines: list) -> dict:
    return {
        AUTOMATION_PIPELINE_RESPONSE_PIPELINES: [
            automation_pipeline_to_response(automation_pipeline)
            for automation_pipeline in automation_pipelines
        ],
    }
