"""Shared helpers for Pipeline 01 - Context Engineering tasks."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


def configure_project_import_path(script_file: str) -> Path:
    """Adds the repository root to sys.path and returns it."""
    project_root = next(
        (parent for parent in Path(script_file).resolve().parents if (parent / "scripts" / "shared").is_dir()),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class ContextEngineeringSupportMixin:
    """Reusable behaviour shared by the small Pipeline 01 tasks."""

    def load_pipeline_config(self) -> dict[str, Any]:
        from scripts.shared.script_json_utils import read_json_file

        configured_path = self.config.get("pipelineConfigPath")
        if not isinstance(configured_path, str) or not configured_path.strip():
            raise ValueError("Task config must contain non-empty string: pipelineConfigPath")
        path = Path(configured_path)
        if not path.is_absolute():
            path = self.project_root / path
        pipeline_config = read_json_file(path)
        if not isinstance(pipeline_config, dict):
            raise ValueError(f"Pipeline config must contain a JSON object: {path}")
        self.pipeline_config_path = path.resolve()
        self.pipeline_task_instance = self._load_pipeline_task_instance()
        return pipeline_config

    def _load_pipeline_task_instance(self) -> dict[str, Any] | None:
        raw_value = os.environ.get("CAUTOMATION_PIPELINE_TASK_INSTANCE")
        if raw_value in (None, ""):
            return None
        value = json.loads(raw_value)
        if not isinstance(value, dict):
            raise ValueError("CAUTOMATION_PIPELINE_TASK_INSTANCE must contain a JSON object.")
        return value

    def task_definition_id(self) -> str:
        if isinstance(getattr(self, "pipeline_task_instance", None), dict):
            value = self.pipeline_task_instance.get("taskDefinitionId")
        else:
            value = self.config.get("taskDefinitionId", self.config.get("taskId"))
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task config or task instance must contain taskDefinitionId.")
        return value

    def pipeline_task_id(self) -> str:
        if isinstance(getattr(self, "pipeline_task_instance", None), dict):
            value = self.pipeline_task_instance.get("pipelineTaskId")
        else:
            value = self.config.get("pipelineTaskId", self.task_definition_id())
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task config or task instance must contain pipelineTaskId.")
        return value

    def task_id(self) -> str:
        return self.task_definition_id()

    def task_version(self) -> str:
        if isinstance(getattr(self, "pipeline_task_instance", None), dict):
            value = self.pipeline_task_instance.get("taskVersion", self.config.get("taskVersion"))
        else:
            value = self.config.get("taskVersion")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task config must contain non-empty string: taskVersion")
        return value

    def pipeline_id(self) -> str:
        value = self.pipeline_config.get("pipelineId")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Pipeline config must contain non-empty string: pipelineId")
        return value

    def project_id(self) -> str:
        value = self.pipeline_config.get("projectId")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Pipeline config must contain non-empty string: projectId")
        return value

    def module_id(self) -> str:
        value = self.pipeline_config.get("moduleId")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Pipeline config must contain non-empty string: moduleId")
        return value

    def group(self, name: str) -> dict[str, Any]:
        value = self.pipeline_config.get(name)
        if not isinstance(value, dict):
            raise ValueError(f"Pipeline config must contain object: {name}")
        return value

    def task_instances(self) -> list[dict[str, Any]]:
        value = self.pipeline_config.get("taskInstances")
        if not isinstance(value, list):
            raise ValueError("Pipeline config must contain a taskInstances array.")
        return [item for item in value if isinstance(item, dict)]

    def pipeline_task_config(self, pipeline_task_id_or_definition_id: str) -> dict[str, Any]:
        for task_instance in self.task_instances():
            if (
                task_instance.get("pipelineTaskId") == pipeline_task_id_or_definition_id
                or task_instance.get("taskDefinitionId") == pipeline_task_id_or_definition_id
            ):
                return task_instance
        raise ValueError(f"Pipeline config does not define task instance: {pipeline_task_id_or_definition_id}")

    def pipeline_task_state_file(self, pipeline_task_id_or_definition_id: str) -> str:
        task_config = self.pipeline_task_config(pipeline_task_id_or_definition_id)
        value = task_config.get("stateFile")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Pipeline task instance config must contain non-empty stateFile: {pipeline_task_id_or_definition_id}")
        return value

    def current_task_state_file(self) -> str:
        if isinstance(getattr(self, "pipeline_task_instance", None), dict):
            value = self.pipeline_task_instance.get("stateFile")
            if isinstance(value, str) and value.strip():
                return value
        return self.pipeline_task_state_file(self.pipeline_task_id())

    def resolve_placeholders(self, value: str) -> str:
        replacements = {
            "projectId": self.project_id(),
            "moduleId": self.module_id(),
            "pipelineId": self.pipeline_id(),
            "pipelineTaskId": self.pipeline_task_id(),
            "taskDefinitionId": self.task_definition_id(),
            "taskId": self.task_id(),
        }
        resolved = value
        for key, replacement in replacements.items():
            resolved = resolved.replace("{" + key + "}", replacement)
        return resolved

    def resolve_project_path(self, configured_path: str) -> Path:
        path = Path(self.resolve_placeholders(configured_path))
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def state_root(self) -> Path:
        configured = self.group("output")["pipelineStateRoot"]
        return self.resolve_project_path(configured)

    def task_reports_directory(self) -> Path:
        configured = self.group("output")["taskReportsDirectory"]
        return self.resolve_project_path(configured)

    def cautomation_root(self) -> Path:
        return self.resolve_project_path(self.group("input")["cautomationRoot"])

    def project_config_path(self) -> Path:
        return self.cautomation_root() / self.resolve_placeholders(self.group("input")["projectConfigPath"])

    def module_input_root(self) -> Path:
        return self.cautomation_root() / self.resolve_placeholders(self.group("input")["moduleInputPath"])

    def contract_paths(self) -> tuple[Path, Path]:
        input_config = self.group("input")
        module_root = self.module_input_root()
        return module_root / input_config["srsFileName"], module_root / input_config["atsFileName"]

    def context_package_dir(self) -> Path:
        output_config = self.group("output")
        package_root = self.cautomation_root() / self.resolve_placeholders(output_config["contextPackageRoot"])
        package_id = self.resolve_placeholders(output_config["contextPackageId"])
        return (package_root / package_id).resolve()

    def ensure_state_root(self) -> Path:
        root = self.state_root()
        root.mkdir(parents=True, exist_ok=True)
        self.task_reports_directory().mkdir(parents=True, exist_ok=True)
        return root

    def state_file(self, file_name: str) -> Path:
        return self.ensure_state_root() / file_name

    def write_state_json(self, file_name: str, payload: dict[str, Any]) -> Path:
        from scripts.shared.script_json_utils import write_json_file

        path = self.state_file(file_name)
        write_json_file(path, payload)
        return path

    def read_state_json(self, file_name: str) -> dict[str, Any]:
        from scripts.shared.script_json_utils import read_json_file

        path = self.state_file(file_name)
        if not path.exists():
            raise FileNotFoundError(f"Required pipeline state file missing: {path}")
        payload = read_json_file(path)
        if not isinstance(payload, dict):
            raise ValueError(f"Pipeline state file must contain a JSON object: {path}")
        return payload

    def write_task_report(self, report: dict[str, Any]) -> Path:
        from scripts.shared.script_json_utils import write_json_file

        report_path = self.write_json_report(report)
        copied_report_path = self.task_reports_directory() / report_path.name
        write_json_file(copied_report_path, report)
        return report_path

    def base_report(self, status: str, started_at_utc: str, elapsed_seconds: float) -> dict[str, Any]:
        return {
            "scriptName": self.script_name,
            "pipelineId": self.pipeline_id(),
            "pipelineTaskId": self.pipeline_task_id(),
            "taskDefinitionId": self.task_definition_id(),
            "taskId": self.task_id(),
            "taskVersion": self.task_version(),
            "status": status,
            "startedAtUtc": started_at_utc,
            "finishedAtUtc": utc_now_iso(),
            "elapsedSeconds": elapsed_seconds,
            "configuration": {
                "taskConfigPath": self.to_project_relative_path(self.config_path),
                "pipelineConfigPath": self.to_project_relative_path(self.pipeline_config_path),
                "projectId": self.project_id(),
                "moduleId": self.module_id(),
                "pipelineTaskId": self.pipeline_task_id(),
                "taskDefinitionId": self.task_definition_id(),
            },
        }

    def status_from(self, warnings: list[dict[str, str]], errors: list[dict[str, str]]) -> str:
        if errors:
            return "FAILED"
        if warnings:
            return "PASSED_WITH_WARNINGS"
        return "PASSED"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_record(script: Any, path: Path, category: str, file_type: str) -> dict[str, Any]:
    return {
        "path": script.to_project_relative_path(path),
        "category": category,
        "file_type": file_type,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def read_docx_as_markdown(path: Path) -> str:
    try:
        with ZipFile(path) as archive:
            xml_bytes = archive.read("word/document.xml")
    except (BadZipFile, KeyError) as exc:
        raise RuntimeError(f"Invalid or unsupported DOCX file: {path}") from exc

    root = ET.fromstring(xml_bytes)
    body = root.find(f"{_WORD_NS}body")
    if body is None:
        return ""

    blocks: list[str] = []
    for child in body:
        if child.tag == f"{_WORD_NS}p":
            text = paragraph_text(child)
            if text:
                blocks.append(text)
        elif child.tag == f"{_WORD_NS}tbl":
            table = table_as_markdown(child)
            if table:
                blocks.append(table)
    return "\n\n".join(blocks).strip() + "\n"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(iter_text_nodes(paragraph)).strip()


def iter_text_nodes(element: ET.Element) -> Iterable[str]:
    for node in element.iter(f"{_WORD_NS}t"):
        if node.text:
            yield node.text


def table_as_markdown(table: ET.Element) -> str:
    rows: list[list[str]] = []
    for row in table.iter(f"{_WORD_NS}tr"):
        cells: list[str] = []
        for cell in row.iter(f"{_WORD_NS}tc"):
            paragraphs = [paragraph_text(p) for p in cell.iter(f"{_WORD_NS}p")]
            value = " ".join(p for p in paragraphs if p).strip()
            cells.append(value.replace("|", "\\|"))
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    max_cols = max(len(row) for row in rows)
    normalized = [row + [""] * (max_cols - len(row)) for row in rows]
    header = normalized[0]
    separator = ["---"] * max_cols
    body = normalized[1:]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(separator) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def clean_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
