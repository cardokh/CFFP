from __future__ import annotations

import hashlib
import importlib
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.ai_generation_engine.ai_generation_contracts import (  # noqa: E402
    LlmGenerationOptions,
    LlmProvider,
    PromptMetadata,
)
from scripts.shared.base_script import BaseScript  # noqa: E402
from scripts.shared.script_json_utils import write_json_file  # noqa: E402


class AiGenerationEngine(BaseScript):
    """
    Reusable AI Generation Engine vertical slice.

    The engine reads only the Iteration 1 master context, sends a prompt through a
    replaceable LLMProvider boundary, and stages any returned artifacts inside an
    isolated workspace. It never writes generated artifacts to live source folders.
    """

    def __init__(self):
        super().__init__(__file__)

    def run(self) -> None:
        started_at = self._utc_now()
        start_counter = perf_counter()

        master_context_path = self._resolve_project_path(self.config["inputs"]["masterContextPath"])
        master_context = self._read_master_context(master_context_path)
        prompt = self._build_prompt(master_context)
        prompt_metadata = self._build_prompt_metadata(master_context_path, master_context, prompt)

        provider = self._build_provider()
        options = LlmGenerationOptions.from_config(self.config.get("provider", {}).get("options", {}))
        provider_result = provider.generate(prompt=prompt, options=options)
        response_sha256 = self._sha256(provider_result.response_text)

        execution_id = self._execution_id(prompt_metadata.prompt_sha256, response_sha256)
        workspace_paths = self._resolve_workspace_paths(execution_id)

        manifest = self._parse_provider_response(provider_result.response_text)
        staged_artifacts = self._stage_artifacts(manifest, workspace_paths["artifactsRoot"])

        finished_at = self._utc_now()
        elapsed_ms = round((perf_counter() - start_counter) * 1000, 3)
        report = self._build_report(
            execution_id=execution_id,
            started_at=started_at,
            finished_at=finished_at,
            elapsed_ms=elapsed_ms,
            master_context_path=master_context_path,
            prompt_metadata=prompt_metadata,
            provider=provider,
            options=options,
            provider_result=provider_result,
            response_sha256=response_sha256,
            manifest=manifest,
            staged_artifacts=staged_artifacts,
            workspace_paths=workspace_paths,
        )

        self._write_text_file(workspace_paths["promptPath"], prompt)
        self._write_text_file(workspace_paths["rawResponsePath"], provider_result.response_text)
        write_json_file(workspace_paths["manifestPath"], manifest)
        write_json_file(workspace_paths["reportPath"], report)

        print(
            f"PASS {self.script_name}: staged {len(staged_artifacts)} artifact(s) "
            f"inside {self.to_project_relative_path(workspace_paths['executionRoot'])}"
        )

    def _read_master_context(self, master_context_path: Path) -> str:
        if not master_context_path.exists():
            raise FileNotFoundError(f"Master context not found: {master_context_path}")
        if not master_context_path.is_file():
            raise ValueError(f"Master context path is not a file: {master_context_path}")
        return master_context_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")

    def _build_prompt(self, master_context: str) -> str:
        prompt_config = self.config.get("prompt", {})
        lines = [
            prompt_config.get("systemInstruction", "Generate staged artifacts from the master context."),
            "",
            "INPUT FIREWALL",
            "- The compiled master-context.md below is the only contextual input.",
            "- Do not use repository files, prior generated files, or unstated assumptions.",
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
                prompt_config.get("requiredOutput", "Return only valid JSON matching the artifact manifest contract."),
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
            prompt_id=self.config.get("prompt", {}).get("promptId", "ai-generation-engine-v1"),
            source_path=self.to_project_relative_path(master_context_path),
            source_sha256=self._sha256(master_context),
            prompt_sha256=self._sha256(prompt),
            character_count=len(prompt),
            line_count=self._line_count(prompt),
        )

    def _build_provider(self) -> LlmProvider:
        provider_config = self.config.get("provider", {})
        provider_class_path = provider_config.get("classPath")
        if not provider_class_path:
            raise ValueError("provider.classPath is required.")

        module_name, class_name = provider_class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class()

    def _parse_provider_response(self, response_text: str) -> dict[str, Any]:
        try:
            manifest = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM provider response must be valid JSON for Iteration 2 staging.") from exc

        if not isinstance(manifest, dict):
            raise ValueError("LLM provider response JSON root must be an object.")
        artifacts = manifest.get("artifacts")
        if artifacts is None:
            manifest["artifacts"] = []
        elif not isinstance(artifacts, list):
            raise ValueError("LLM provider response field artifacts must be a list when present.")
        return manifest

    def _stage_artifacts(self, manifest: dict[str, Any], artifacts_root: Path) -> list[dict[str, Any]]:
        staged_artifacts = []
        seen_target_paths: set[str] = set()

        for index, artifact in enumerate(manifest.get("artifacts", []), start=1):
            if not isinstance(artifact, dict):
                raise ValueError(f"Artifact {index} must be an object.")

            target_path = self._normalize_target_path(artifact.get("targetPath"), index)
            if target_path in seen_target_paths:
                raise ValueError(f"Duplicate artifact targetPath detected: {target_path}")
            seen_target_paths.add(target_path)

            staged_path = self._safe_join(artifacts_root, target_path)
            content = str(artifact.get("content", ""))
            self._write_text_file(staged_path, content)
            staged_artifacts.append(
                {
                    "artifactType": artifact.get("artifactType", "unspecified"),
                    "targetPath": target_path,
                    "stagedPath": self.to_project_relative_path(staged_path),
                    "sha256": self._sha256(content),
                    "sizeBytes": len(content.encode("utf-8")),
                    "lineCount": self._line_count(content),
                    "reason": artifact.get("reason", ""),
                }
            )
        return staged_artifacts

    def _normalize_target_path(self, value: Any, artifact_index: int) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Artifact {artifact_index} must define a non-empty targetPath string.")
        target_path = value.replace("\\", "/").strip("/")
        path = Path(target_path)
        if path.is_absolute():
            raise ValueError(f"Artifact {artifact_index} targetPath must be repository-relative.")
        if ".." in path.parts:
            raise ValueError(f"Artifact {artifact_index} targetPath must not contain path traversal.")
        return target_path

    def _safe_join(self, root: Path, relative_path: str) -> Path:
        root_resolved = root.resolve()
        candidate = (root / relative_path).resolve()
        if root_resolved != candidate and root_resolved not in candidate.parents:
            raise ValueError(f"Staged artifact path escapes workspace: {relative_path}")
        return candidate

    def _resolve_workspace_paths(self, execution_id: str) -> dict[str, Path]:
        workspace_template = self.config.get("outputs", {}).get(
            "stagingRoot",
            ".ccore_workspace/staging/{executionId}",
        )
        execution_root = self._resolve_project_path(workspace_template.replace("{executionId}", execution_id))
        return {
            "executionRoot": execution_root,
            "artifactsRoot": execution_root / "artifacts",
            "promptPath": execution_root / "prompt.txt",
            "rawResponsePath": execution_root / "raw_response.txt",
            "manifestPath": execution_root / "artifact_manifest.json",
            "reportPath": execution_root / "generation_report.json",
        }

    def _resolve_project_path(self, relative_path: str) -> Path:
        path = Path(relative_path)
        if path.is_absolute():
            raise ValueError(f"Configured path must be project-relative: {relative_path}")
        if ".." in path.parts:
            raise ValueError(f"Configured path must not contain path traversal: {relative_path}")
        return (self.project_root / path).resolve()

    def _build_report(
        self,
        *,
        execution_id: str,
        started_at: str,
        finished_at: str,
        elapsed_ms: float,
        master_context_path: Path,
        prompt_metadata: PromptMetadata,
        provider: LlmProvider,
        options: LlmGenerationOptions,
        provider_result: Any,
        response_sha256: str,
        manifest: dict[str, Any],
        staged_artifacts: list[dict[str, Any]],
        workspace_paths: dict[str, Path],
    ) -> dict[str, Any]:
        return {
            "reportType": "ai-generation-engine",
            "reportVersion": "2.0",
            "status": "PASSED",
            "executionId": execution_id,
            "timestamps": {
                "startedAt": started_at,
                "finishedAt": finished_at,
                "elapsedMs": elapsed_ms,
            },
            "inputFirewall": {
                "allowedInput": self.to_project_relative_path(master_context_path),
                "sourceSha256": prompt_metadata.source_sha256,
            },
            "prompt": prompt_metadata.to_dict(),
            "provider": {
                "configuredType": self.config.get("provider", {}).get("type"),
                "configuredClassPath": self.config.get("provider", {}).get("classPath"),
                "runtimeProviderId": provider.provider_id,
                "options": options.to_dict(),
                "result": provider_result.to_report_dict(response_sha256),
            },
            "workspace": {
                key: self.to_project_relative_path(value)
                for key, value in workspace_paths.items()
            },
            "manifest": {
                "manifestVersion": manifest.get("manifestVersion"),
                "artifactCount": len(staged_artifacts),
                "rawResponseSha256": response_sha256,
            },
            "stagedArtifacts": staged_artifacts,
            "safety": {
                "liveSourceWriteAllowed": False,
                "stagingIsolation": "All generated artifacts are written under the execution artifacts workspace only.",
                "liveSourceRootsTouched": [],
            },
        }

    def _execution_id(self, prompt_sha256: str, response_sha256: str) -> str:
        seed = f"{self.config.get('generationName', self.script_name)}:{prompt_sha256}:{response_sha256}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

    def _write_text_file(self, file_path: Path, content: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8", newline="\n")

    def _sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _line_count(self, content: str) -> int:
        if content == "":
            return 0
        return content.count("\n") + (0 if content.endswith("\n") else 1)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    AiGenerationEngine().run()
