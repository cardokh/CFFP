from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.ai_generation_engine.ai_generation_contracts import PromptMetadata
from scripts.shared.base_script import BaseScript
from scripts.shared.script_json_utils import write_json_file


class AiGenerationEngine(BaseScript):
    """Generates staged artifact manifests from the compiled master context."""

    def __init__(self):
        super().__init__(__file__)

    def run(self) -> None:
        timing_mode = self.config.get("timing", {}).get("mode", "measured")
        start = perf_counter()

        master_context_path = self.project_root / self.config["inputs"]["masterContextPath"]
        master_context = self._read_master_context(master_context_path)
        prompt = self._build_prompt(master_context)
        prompt_metadata = self._build_prompt_metadata(master_context_path, master_context, prompt)

        provider = self._build_provider()
        provider_response = provider.generate(
            prompt=prompt,
            prompt_metadata=prompt_metadata,
            provider_config=self.config.get("provider", {}).get("config", {}),
        )

        manifest = self._parse_manifest(provider_response.response_text)
        execution_id = self._execution_id(prompt_metadata.prompt_sha256, provider_response.response_sha256)
        staging_paths = self._resolve_staging_paths(execution_id)
        staged_artifacts = self._stage_artifacts(manifest, staging_paths["filesRoot"])
        validation = self._validate_staged_artifacts(staged_artifacts)

        elapsed_ms = (perf_counter() - start) * 1000
        timing = self._build_timing(timing_mode, elapsed_ms)
        report = self._build_report(
            execution_id=execution_id,
            master_context_path=master_context_path,
            prompt_metadata=prompt_metadata,
            provider_response=provider_response,
            manifest=manifest,
            staging_paths=staging_paths,
            staged_artifacts=staged_artifacts,
            validation=validation,
            timing=timing,
        )

        self._write_text_file(staging_paths["promptPath"], prompt)
        write_json_file(staging_paths["manifestPath"], manifest)
        write_json_file(staging_paths["reportPath"], report)

        print(
            f"PASS {self.script_name}: generated {len(staged_artifacts)} staged artifact(s) for execution {execution_id}"
        )

    def _read_master_context(self, master_context_path: Path) -> str:
        if not master_context_path.exists():
            raise FileNotFoundError(f"Master context not found: {master_context_path}")
        return master_context_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")

    def _build_prompt(self, master_context: str) -> str:
        prompt_config = self.config.get("prompt", {})
        lines = [
            prompt_config.get("systemInstruction", "Generate artifacts from the compiled master context."),
            "",
            "NON-NEGOTIABLE RULES",
        ]
        for rule in prompt_config.get("rules", []):
            lines.append(f"- {rule}")
        lines.extend(
            [
                "",
                "COMPILED MASTER CONTEXT",
                master_context.rstrip("\n"),
                "",
                "REQUIRED OUTPUT",
                prompt_config.get("requiredOutput", "Return valid JSON matching the artifact manifest contract."),
                "",
            ]
        )
        return "\n".join(lines)

    def _build_prompt_metadata(
        self,
        master_context_path: Path,
        master_context: str,
        prompt: str,
    ) -> PromptMetadata:
        return PromptMetadata(
            prompt_id=self.config.get("prompt", {}).get("promptId", "generate-crud-module-from-master-context"),
            source_path=self.to_project_relative_path(master_context_path),
            source_sha256=self._sha256(master_context),
            prompt_sha256=self._sha256(prompt),
            character_count=len(prompt),
            line_count=self._line_count(prompt),
        )

    def _build_provider(self):
        provider_config = self.config.get("provider", {})
        provider_class_path = provider_config.get("classPath")
        if not provider_class_path:
            raise ValueError("AI generation provider.classPath is not configured.")

        module_name, class_name = provider_class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class()

    def _parse_manifest(self, response_text: str) -> dict:
        try:
            manifest = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise ValueError("AI provider response was not valid JSON.") from exc

        if not isinstance(manifest, dict):
            raise ValueError("AI provider response JSON root must be an object.")
        if "artifacts" not in manifest or not isinstance(manifest["artifacts"], list):
            raise ValueError("AI provider manifest must contain an artifacts array.")
        return manifest

    def _execution_id(self, prompt_sha256: str, response_sha256: str) -> str:
        seed = f"{self.config.get('generationName', self.script_name)}:{prompt_sha256}:{response_sha256}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

    def _resolve_staging_paths(self, execution_id: str) -> dict[str, Path]:
        staging_root_template = self.config.get("outputs", {}).get(
            "stagingRoot",
            "generated/automation_factory/{executionId}",
        )
        staging_root = self.project_root / staging_root_template.replace("{executionId}", execution_id)
        return {
            "stagingRoot": staging_root,
            "filesRoot": staging_root / "files",
            "manifestPath": staging_root / "artifact_manifest.json",
            "reportPath": staging_root / "generation_report.json",
            "promptPath": staging_root / "prompt.txt",
        }

    def _stage_artifacts(self, manifest: dict, files_root: Path) -> list[dict]:
        staged_artifacts = []
        for index, artifact in enumerate(manifest.get("artifacts", []), start=1):
            target_path = artifact.get("targetPath", "")
            if not target_path or Path(target_path).is_absolute():
                raise ValueError(f"Artifact {index} has invalid repository-relative targetPath.")
            if ".." in Path(target_path).parts:
                raise ValueError(f"Artifact {index} targetPath escapes staging root.")

            staged_path = files_root / target_path
            content = artifact.get("content", "")
            self._write_text_file(staged_path, content)
            staged_artifacts.append(
                {
                    "artifactType": artifact.get("artifactType", "unspecified"),
                    "targetPath": target_path,
                    "stagedPath": self.to_project_relative_path(staged_path),
                    "sha256": self._sha256(content),
                    "sizeBytes": len(content.encode("utf-8")),
                    "lineCount": self._line_count(content),
                }
            )
        return staged_artifacts

    def _validate_staged_artifacts(self, staged_artifacts: list[dict]) -> dict:
        findings = []
        for artifact in staged_artifacts:
            staged_path = self.project_root / artifact["stagedPath"]
            if not staged_path.exists():
                findings.append(
                    self._finding("FAILED", "ERROR", artifact["stagedPath"], "Staged artifact is missing.")
                )
                continue

            if staged_path.suffix == ".py":
                compile_result = self._compile_python_file(staged_path)
                if compile_result is not None:
                    findings.append(
                        self._finding("FAILED", "ERROR", artifact["stagedPath"], compile_result)
                    )
                else:
                    findings.append(
                        self._finding("PASSED", "INFO", artifact["stagedPath"], "Python file compiles.")
                    )

        status = "PASSED"
        if any(finding["status"] == "FAILED" for finding in findings):
            status = "FAILED"
        return {
            "status": status,
            "findingCount": len(findings),
            "findings": findings,
        }

    def _compile_python_file(self, file_path: Path) -> str | None:
        try:
            compile(file_path.read_text(encoding="utf-8"), str(file_path), "exec")
        except SyntaxError as exc:
            return f"Python compile failed: {exc}"
        return None

    def _build_timing(self, timing_mode: str, elapsed_ms: float) -> dict:
        if timing_mode == "deterministic":
            return {
                "mode": "deterministic",
                "elapsedMilliseconds": 0,
                "measuredElapsedMillisecondsAvailable": True,
                "measuredElapsedMillisecondsOmittedForDeterminism": True,
            }
        return {
            "mode": "measured",
            "elapsedMilliseconds": round(elapsed_ms, 3),
            "measuredElapsedMillisecondsAvailable": True,
            "measuredElapsedMillisecondsOmittedForDeterminism": False,
        }

    def _build_report(
        self,
        *,
        execution_id: str,
        master_context_path: Path,
        prompt_metadata: PromptMetadata,
        provider_response,
        manifest: dict,
        staging_paths: dict[str, Path],
        staged_artifacts: list[dict],
        validation: dict,
        timing: dict,
    ) -> dict:
        return {
            "generationEngine": {
                "name": self.config.get("generationName", self.script_name),
                "version": self.config.get("generationVersion", "1.0"),
                "target": self.config.get("target", "unspecified"),
            },
            "summary": {
                "status": validation["status"],
                "executionId": execution_id,
                "artifactCount": len(staged_artifacts),
                "stagingRoot": self.to_project_relative_path(staging_paths["stagingRoot"]),
                "manifestPath": self.to_project_relative_path(staging_paths["manifestPath"]),
                "generationReportPath": self.to_project_relative_path(staging_paths["reportPath"]),
            },
            "input": {
                "masterContextPath": self.to_project_relative_path(master_context_path),
                "masterContextSha256": prompt_metadata.source_sha256,
            },
            "promptMetadata": {
                "promptId": prompt_metadata.prompt_id,
                "sourcePath": prompt_metadata.source_path,
                "sourceSha256": prompt_metadata.source_sha256,
                "promptSha256": prompt_metadata.prompt_sha256,
                "characterCount": prompt_metadata.character_count,
                "lineCount": prompt_metadata.line_count,
            },
            "modelMetadata": provider_response.model_metadata,
            "providerMetadata": {
                "providerId": provider_response.provider_id,
                "finishReason": provider_response.finish_reason,
                "responseSha256": provider_response.response_sha256,
                "usage": provider_response.usage_metadata,
            },
            "timing": timing,
            "generatedArtifacts": staged_artifacts,
            "validation": validation,
            "manifestSummary": {
                "manifestVersion": manifest.get("manifestVersion"),
                "requiredManualDecisionCount": len(manifest.get("requiredManualDecisions", [])),
                "validationHintCount": len(manifest.get("validationHints", [])),
                "generationNoteCount": len(manifest.get("generationNotes", [])),
            },
        }

    def _write_text_file(self, file_path: Path, content: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8", newline="\n")

    def _finding(self, status: str, severity: str, path: str, message: str) -> dict:
        return {
            "status": status,
            "severity": severity,
            "path": path,
            "message": message,
        }

    def _sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _line_count(self, content: str) -> int:
        if content == "":
            return 0
        return content.count("\n") + (0 if content.endswith("\n") else 1)


if __name__ == "__main__":
    AiGenerationEngine().run()
