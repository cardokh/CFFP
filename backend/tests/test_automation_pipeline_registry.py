"""
Automation pipeline registry tests.

Responsibilities:
- Verify JSON-based automation pipeline discovery.
- Verify pipeline detail lookup by id.
- Protect the separation between task registry and pipeline registry.
"""

import json

from src.core.automation.automation_pipeline_registry import AutomationPipelineRegistry


def write_registry(registry_path, pipelines) -> None:
    registry_path.write_text(
        json.dumps(
            {
                "pipelines": pipelines,
            }
        ),
        encoding="utf-8",
    )


def build_pipeline_entry(pipeline_id="validate-automation-task") -> dict:
    return {
        "id": pipeline_id,
        "name": "Validate Automation Task",
        "description": "Validates an automation task.",
        "category": "validation",
        "status": "ready",
        "version": "1.0",
        "execution_mode": "sequential",
        "failure_strategy": "stop_on_first_failure",
        "steps": [
            {
                "id": "inspect-script-governance",
                "order": 1,
                "name": "Inspect Script Governance",
                "task_id": "inspect-script-governance",
                "required": True,
            }
        ],
    }


def test_find_all_pipelines_returns_registered_pipelines(tmp_path) -> None:
    registry_path = tmp_path / "automation_pipeline_registry.json"

    write_registry(
        registry_path=registry_path,
        pipelines=[build_pipeline_entry()],
    )

    registry = AutomationPipelineRegistry(registry_path=registry_path)

    pipelines = registry.find_all_pipelines()

    assert len(pipelines) == 1
    assert pipelines[0].pipeline_id == "validate-automation-task"
    assert pipelines[0].name == "Validate Automation Task"
    assert pipelines[0].category == "validation"
    assert pipelines[0].status == "ready"
    assert pipelines[0].execution_mode == "sequential"
    assert pipelines[0].failure_strategy == "stop_on_first_failure"
    assert len(pipelines[0].steps) == 1
    assert pipelines[0].steps[0].task_id == "inspect-script-governance"


def test_find_all_pipelines_returns_empty_list_when_registry_has_no_pipelines(tmp_path) -> None:
    registry_path = tmp_path / "automation_pipeline_registry.json"

    registry_path.write_text(
        json.dumps({}),
        encoding="utf-8",
    )

    registry = AutomationPipelineRegistry(registry_path=registry_path)

    assert registry.find_all_pipelines() == []


def test_find_pipeline_by_id_returns_matching_pipeline(tmp_path) -> None:
    registry_path = tmp_path / "automation_pipeline_registry.json"

    write_registry(
        registry_path=registry_path,
        pipelines=[
            build_pipeline_entry("validate-automation-task"),
            build_pipeline_entry("release-readiness"),
        ],
    )

    registry = AutomationPipelineRegistry(registry_path=registry_path)

    pipeline = registry.find_pipeline_by_id("release-readiness")

    assert pipeline is not None
    assert pipeline.pipeline_id == "release-readiness"


def test_find_pipeline_by_id_returns_none_for_unknown_pipeline(tmp_path) -> None:
    registry_path = tmp_path / "automation_pipeline_registry.json"

    write_registry(
        registry_path=registry_path,
        pipelines=[build_pipeline_entry()],
    )

    registry = AutomationPipelineRegistry(registry_path=registry_path)

    assert registry.find_pipeline_by_id("missing-pipeline") is None
