"""Backend CRUD automation coordinator."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.factory.crud.backend.generator_lib.backend_artifacts import PipelineBackendArtifactBuilder
from scripts.factory.crud.backend.generator_lib.backend_wiring import patch_application_wiring
from scripts.factory.crud.backend.generator_lib.file_writer import write_text_file
from scripts.factory.crud.backend.generator_lib.report_writer import utc_timestamp, write_report
from scripts.factory.crud.backend.generator_lib.template_registry import BackendTemplateRegistry


class BackendCrudGenerator:
    def __init__(self, script_directory: Path):
        self.script_directory = script_directory
        self.template_registry = BackendTemplateRegistry(script_directory / "templates")
        self.pipeline_artifact_builder = PipelineBackendArtifactBuilder(self.template_registry)

    def generate(self, repo_root: Path, config: dict[str, Any]) -> dict[str, Any]:
        entity = config.get("entity")
        if entity != "pipelines":
            raise ValueError("Backend CRUD automation currently supports entity='pipelines' only.")

        output_package_directory = str(config["outputPackageDirectory"])
        overwrite = bool(config.get("options", {}).get("overwriteExistingFiles", True))
        patch_wiring = bool(config.get("options", {}).get("patchApplicationWiring", True))

        file_results = []
        for artifact in self.pipeline_artifact_builder.build_artifacts(output_package_directory):
            result = write_text_file(
                repo_root=repo_root,
                relative_path=artifact.relative_path,
                content=artifact.content,
                overwrite=overwrite,
            )
            file_results.append(result.__dict__)

        patch_results = []
        if patch_wiring:
            patch_results = [result.__dict__ for result in patch_application_wiring(repo_root)]

        report = {
            "scriptName": "generate_backend",
            "entity": entity,
            "status": "passed",
            "generatedAt": utc_timestamp(),
            "outputPackageDirectory": output_package_directory,
            "files": file_results,
            "patchedFiles": patch_results,
        }
        write_report(repo_root, config.get("reportPath"), report)
        return report
