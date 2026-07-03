"""Transforms existing Tasks frontend files into Pipeline frontend files.

The Tasks module remains the golden template.  This transformer keeps the
same HTML structure, CSS classes, JavaScript table/search/sort/pagination
patterns, and only substitutes entity metadata.
"""
from __future__ import annotations

from pathlib import Path

from .config_loader import EntityConfig


def _replace_task_terms(content: str, entity: EntityConfig) -> str:
    replacements = [
        ("CCore Tasks", "CCore Pipelines"),
        ("CCore tasks", "CCore pipelines"),
        ("CCore task", "CCore pipeline"),
        ("ccoreTasks", "ccorePipelines"),
        ("ccoreTask", "ccorePipeline"),
        ("CCORE_TASKS", "CCORE_PIPELINES"),
        ("CCORE_TASK", "CCORE_PIPELINE"),
        ("CCoreTasks", "CCorePipelines"),
        ("CCoreTask", "CCorePipeline"),
        ("ccore-tasks", "ccore-pipelines"),
        ("ccore-task", "ccore-pipeline"),
        ("tasks.html", "pipelines.html"),
        ("task-details.html", "pipeline-details.html"),
        ("tasks.css", "pipelines.css"),
        ("tasks.js", "pipelines.js"),
        ("task-details.css", "pipeline-details.css"),
        ("task-details.js", "pipeline-details.js"),
        ("Tasks", "Pipelines"),
        ("Task", "Pipeline"),
        ("tasks", "pipelines"),
        ("task", "pipeline"),
        ("ccore_pipeliness", "ccore_pipelines"),
        ("Pipeliness", "Pipelines"),
        ("pipelinesName", "pipelineName"),
        ("pipelinesId", "pipelineId"),
        ("pipelinesStatus", "pipelineStatus"),
        ("pipelinesStatusLabel", "pipelineStatusLabel"),
    ]
    result = content
    for source, target in replacements:
        result = result.replace(source, target)
    result = result.replace("Create/Read/Update/ and Delete", "Create/Read/Update/Delete")
    result = result.replace("ccore_pipelines stored", f"{entity.table_name}</code>.") if False else result
    return result


def build_list_html(tasks_html: str, entity: EntityConfig) -> str:
    html = _replace_task_terms(tasks_html, entity)
    html = html.replace("<code>ccore_pipelines</code>", f"<code>{entity.table_name}</code>")
    html = html.replace("Pipeline Name", "Pipeline Name")
    html = html.replace("Name\n                                            </button>", "Pipeline Name\n                                            </button>")
    html = html.replace("placeholder=\"Search pipelines...\"", "placeholder=\"Search pipelines...\"")
    return html


def build_list_css(tasks_css: str, entity: EntityConfig) -> str:
    return _replace_task_terms(tasks_css, entity)


def build_list_js(tasks_js: str, entity: EntityConfig) -> str:
    js = _replace_task_terms(tasks_js, entity)
    field_replacements = {
        "pipelineId": entity.id_field,
        "pipelineName": entity.name_field,
        "pipelineStatusId": entity.status_id_field,
        "pipelineStatusLabel": entity.status_label_field,
        "createdAt": entity.created_at_field,
        "statusLabel": entity.status_label_field,
        "status": entity.status_label_field,
    }
    # The broad Task->Pipeline replacement produces the right identifiers, but
    # the backend contract uses pipelineStatusLabel instead of statusLabel.
    js = js.replace("data-sort-key=\"pipelineName\"", "data-sort-key=\"pipelineName\"")
    js = js.replace("statusLabel", entity.status_label_field)
    js = js.replace("pipeline.status", f"pipeline.{entity.status_label_field}")
    js = js.replace("pipeline.pipelineStatusLabelLabel", "pipeline.pipelineStatusLabel")
    js = js.replace("responseData.pipelines", f"responseData.{entity.api_list_property}")
    js = js.replace("CCORE_API_ENDPOINTS.pipelines.list", f"CCORE_API_ENDPOINTS.{entity.api_key}.list")
    return js


def read_golden_file(tasks_module_dir: Path, relative_path: str) -> str:
    path = tasks_module_dir / relative_path
    return path.read_text(encoding="utf-8")
