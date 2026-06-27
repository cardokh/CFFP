"""Pipeline backend artifact generation."""
from __future__ import annotations

from dataclasses import dataclass

from .template_registry import BackendTemplateRegistry


@dataclass(frozen=True)
class BackendArtifact:
    relative_path: str
    content: str


PIPELINE_TEMPLATE_MAP: dict[str, str] = {
    "__init__.py": "__init__.py.tmpl",
    "pipeline.py": "pipeline.py.tmpl",
    "pipeline_constants.py": "pipeline_constants.py.tmpl",
    "pipeline_messages.py": "pipeline_messages.py.tmpl",
    "pipeline_contracts.py": "pipeline_contracts.py.tmpl",
    "pipeline_mapper.py": "pipeline_mapper.py.tmpl",
    "pipeline_validator.py": "pipeline_validator.py.tmpl",
    "pipeline_repository_contract.py": "pipeline_repository_contract.py.tmpl",
    "pipeline_repository.py": "pipeline_repository.py.tmpl",
    "pipeline_service.py": "pipeline_service.py.tmpl",
    "pipeline_routes.py": "pipeline_routes.py.tmpl",
}


class PipelineBackendArtifactBuilder:
    def __init__(self, template_registry: BackendTemplateRegistry):
        self.template_registry = template_registry

    def build_artifacts(self, output_package_directory: str) -> list[BackendArtifact]:
        artifacts: list[BackendArtifact] = []
        for output_file_name, template_name in PIPELINE_TEMPLATE_MAP.items():
            content = self.template_registry.load_template(template_name)
            artifacts.append(
                BackendArtifact(
                    relative_path=f"{output_package_directory.rstrip('/')}/{output_file_name}",
                    content=content,
                )
            )
        return artifacts
