"""Automation Factory pipeline orchestration."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import DEFAULT_EXECUTION_PROVIDER
from .contracts import (
    ArtifactWriter,
    FactoryConfigRepository,
    LlmProviderFactory,
    PromptBuilder,
    RepositoryContextProviderFactory,
    ReportWriter,
    ValidationProvider,
)
from .report_builder import configuration_snapshot, create_running_report, passed_validations
from .reporting import utc_now_iso
from .repository_context_config import disabled_repository_context_config


@dataclass(frozen=True)
class StandardFactoryPipeline:
    """Coordinates one local Factory execution."""

    config_repository: FactoryConfigRepository
    llm_provider_factory: LlmProviderFactory
    prompt_builder: PromptBuilder
    artifact_writer: ArtifactWriter
    report_writer: ReportWriter
    validation_provider: ValidationProvider
    repository_context_provider_factory: RepositoryContextProviderFactory

    def execute(
        self,
        project_root: Path,
        config_path: Path | None = None,
    ) -> dict[str, Any]:
        execution_id = str(uuid.uuid4())
        report = create_running_report(execution_id, project_root)
        config = None

        try:
            config = self.config_repository.load_config(project_root, config_path)
            if config.execution_provider != DEFAULT_EXECUTION_PROVIDER:
                raise ValueError(f"Unsupported execution provider: {config.execution_provider}")

            task_definition = self.config_repository.load_task_definition(
                project_root, config.task_definition
            )
            report["configuration"] = configuration_snapshot(config, task_definition)

            feature_request = task_definition.input_file.read_text(encoding="utf-8")
            context_config = task_definition.repository_context or disabled_repository_context_config()
            context_provider = self.repository_context_provider_factory.create_provider(project_root)
            repository_context = context_provider.collect_context(context_config)
            report["repository_context"] = repository_context.to_report_snapshot()

            prompt = self.prompt_builder.build_prompt(
                task_definition,
                feature_request,
                repository_context,
            )
            llm_provider = self.llm_provider_factory.create_provider(
                config.llm_provider,
                config.llm_model,
            )
            generated_text = llm_provider.generate_text(prompt)
            self.validation_provider.validate_generated_text(
                generated_text,
                task_definition.artifact.max_output_characters,
            )
            artifact_metadata = self.artifact_writer.write_artifact(task_definition, generated_text)

            report["status"] = "COMPLETED"
            report["artifacts"].append(artifact_metadata)
            report["validation"] = passed_validations(task_definition)
            return report

        except Exception as exc:  # noqa: BLE001 - Factory executions must always report failures.
            report["status"] = "FAILED"
            report["errors"].append({"type": exc.__class__.__name__, "message": str(exc)})
            raise

        finally:
            report["completed_at"] = utc_now_iso()
            report_dir = config.report_dir if config else project_root / "runtime" / "factory" / "reports"
            report_path = self.report_writer.write_report(report_dir, execution_id, report)
            print(f"Execution report written to: {report_path}")
