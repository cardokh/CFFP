"""Run the CCore Automation Factory POC v3.

This POC performs one harmless, configuration-driven automation flow:
load factory configuration, load an automation task definition, read input,
build a prompt, call a configured LLM provider, write one controlled artifact,
validate it, and produce a JSON execution report.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Any

try:
    from prefect import flow, get_run_logger, task
except ImportError:  # Allows compile/smoke validation before Prefect is installed.

    def task(*_args: Any, **_kwargs: Any):  # type: ignore[no-redef]
        def decorator(func):
            return func

        return decorator

    def flow(*_args: Any, **_kwargs: Any):  # type: ignore[no-redef]
        def decorator(func):
            return func

        return decorator

    def get_run_logger():  # type: ignore[no-redef]
        class ConsoleLogger:
            def info(self, message: str, *args: Any) -> None:
                print(message % args if args else message)

            def error(self, message: str, *args: Any) -> None:
                print(message % args if args else message, file=sys.stderr)

        return ConsoleLogger()

from .config import load_config, load_task_definition
from .llm_provider import create_llm_provider
from .models import AutomationTaskDefinition, FactoryConfig
from .reporting import utc_now_iso, write_execution_report
from .validation import (
    validate_artifact_path,
    validate_generated_text,
    validate_written_artifact,
)


@task(name="Load Factory Configuration")
def load_factory_configuration(project_root: Path, config_path: Path | None = None) -> FactoryConfig:
    logger = get_run_logger()
    config = load_config(project_root, config_path)
    logger.info("Loaded factory configuration: %s", config.factory_name)
    return config


@task(name="Load Automation Task Definition")
def load_automation_task_definition(
    project_root: Path, config: FactoryConfig
) -> AutomationTaskDefinition:
    logger = get_run_logger()
    task_definition = load_task_definition(project_root, config.task_definition)
    logger.info("Loaded automation task definition: %s", task_definition.task_id)
    return task_definition


@task(name="Read Feature Request")
def read_feature_request(task_definition: AutomationTaskDefinition) -> str:
    logger = get_run_logger()
    text = task_definition.input_file.read_text(encoding="utf-8")
    logger.info("Read feature request from %s", task_definition.input_file)
    return text


@task(name="Build Prompt")
def build_prompt(task_definition: AutomationTaskDefinition, feature_request: str) -> str:
    logger = get_run_logger()
    template = task_definition.prompt_template.read_text(encoding="utf-8")
    prompt = template.replace("{{FEATURE_REQUEST}}", feature_request.strip())
    logger.info("Built prompt from template %s", task_definition.prompt_template)
    return prompt


@task(name="Generate Artifact Text", retries=2, retry_delay_seconds=10)
def generate_artifact_text(
    config: FactoryConfig, task_definition: AutomationTaskDefinition, prompt: str
) -> str:
    logger = get_run_logger()
    provider = create_llm_provider(config.llm_provider, config.gemini_model)
    logger.info("Calling configured LLM provider: %s", config.llm_provider)
    generated_text = provider.generate_text(prompt)
    validate_generated_text(generated_text, task_definition.artifact.max_output_characters)
    logger.info("Generated artifact text passed validation")
    return generated_text


@task(name="Write Controlled Artifact")
def write_controlled_artifact(
    task_definition: AutomationTaskDefinition, generated_text: str
) -> dict[str, object]:
    logger = get_run_logger()
    artifact_definition = task_definition.artifact
    artifact_definition.output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_definition.output_dir / artifact_definition.filename

    validate_artifact_path(
        artifact_definition.output_dir,
        artifact_path,
        artifact_definition.allowed_extensions,
    )
    artifact_path.write_text(generated_text, encoding="utf-8")
    artifact_metadata = validate_written_artifact(artifact_path)

    logger.info("Wrote controlled artifact: %s", artifact_path)
    return artifact_metadata


def _configuration_snapshot(config: FactoryConfig, task_definition: AutomationTaskDefinition) -> dict[str, Any]:
    return {
        "factory_name": config.factory_name,
        "execution_provider": config.execution_provider,
        "llm_provider": config.llm_provider,
        "gemini_model": config.gemini_model,
        "task_definition_path": str(config.task_definition),
        "task_id": task_definition.task_id,
        "task_name": task_definition.name,
        "input_file": str(task_definition.input_file),
        "prompt_template": str(task_definition.prompt_template),
        "output_dir": str(task_definition.artifact.output_dir),
        "artifact_filename": task_definition.artifact.filename,
        "allowed_output_extensions": list(task_definition.artifact.allowed_extensions),
        "max_output_characters": task_definition.artifact.max_output_characters,
        "configured_validations": list(task_definition.validations),
    }


def _passed_validations(task_definition: AutomationTaskDefinition) -> list[dict[str, str]]:
    return [{"name": validation_name, "status": "PASSED"} for validation_name in task_definition.validations]


@flow(name="CCore Automation Factory POC v3")
def run_factory_pipeline(
    project_root_value: str | None = None,
    config_path_value: str | None = None,
) -> dict[str, Any]:
    """Execute one local CCore factory workflow and always write a report."""

    project_root = Path(project_root_value).resolve() if project_root_value else Path(__file__).resolve().parent
    config_path = Path(config_path_value).resolve() if config_path_value else None
    execution_id = str(uuid.uuid4())
    started_at = utc_now_iso()
    report: dict[str, Any] = {
        "execution_id": execution_id,
        "status": "RUNNING",
        "started_at": started_at,
        "completed_at": None,
        "project_root": str(project_root),
        "configuration": {},
        "artifacts": [],
        "validation": [],
        "errors": [],
    }

    config: FactoryConfig | None = None

    try:
        config = load_factory_configuration(project_root, config_path)
        if config.execution_provider != "prefect":
            raise ValueError(f"Unsupported execution provider: {config.execution_provider}")

        task_definition = load_automation_task_definition(project_root, config)
        report["configuration"] = _configuration_snapshot(config, task_definition)

        feature_request = read_feature_request(task_definition)
        prompt = build_prompt(task_definition, feature_request)
        generated_text = generate_artifact_text(config, task_definition, prompt)
        artifact_metadata = write_controlled_artifact(task_definition, generated_text)

        report["status"] = "COMPLETED"
        report["artifacts"].append(artifact_metadata)
        report["validation"] = _passed_validations(task_definition)
        return report

    except Exception as exc:  # noqa: BLE001 - this POC must always produce an execution report.
        report["status"] = "FAILED"
        report["errors"].append(
            {
                "type": exc.__class__.__name__,
                "message": str(exc),
            }
        )
        raise

    finally:
        report["completed_at"] = utc_now_iso()
        report_dir = config.report_dir if config else project_root / "reports"
        report_path = write_execution_report(report_dir, execution_id, report)
        print(f"Execution report written to: {report_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CCore Automation Factory POC v3.")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Optional path to factory_config.json.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_factory_pipeline(project_root_value=args.project_root, config_path_value=args.config)
