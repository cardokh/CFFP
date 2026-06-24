from __future__ import annotations

import json
from typing import Any

from scripts.factory.ai_generation_engine.ai_generation_contracts import (
    LlmGenerationOptions,
    LlmGenerationResult,
)


class StaticManifestLlmProvider:
    """
    Deterministic local provider for safe engine verification.

    This provider intentionally does not generate application module code. It returns a
    configurable artifact manifest so the AI Generation Engine can be tested without
    coupling the engine to Gemini, OpenAI, or any other vendor SDK.
    """

    provider_id = "static-manifest-provider"

    def generate(
        self,
        *,
        prompt: str,
        options: LlmGenerationOptions,
    ) -> LlmGenerationResult:
        manifest = self._build_manifest(options.extra)
        response_text = json.dumps(
            manifest,
            indent=4,
            sort_keys=True,
        )

        return LlmGenerationResult(
            provider_id=self.provider_id,
            model_metadata={
                "model": options.model or "static-manifest-v1",
                "vendor": "local",
                "mode": "deterministic-test-double",
            },
            response_text=response_text,
            finish_reason="completed",
            usage_metadata={
                "promptCharacters": len(prompt),
                "responseCharacters": len(response_text),
            },
        )

    def _build_manifest(self, extra_options: dict[str, Any]) -> dict[str, Any]:
        configured_artifacts = extra_options.get("artifacts", [])
        if not isinstance(configured_artifacts, list):
            raise ValueError("StaticManifestLlmProvider extra.artifacts must be a list.")

        artifacts = []
        for index, artifact in enumerate(configured_artifacts, start=1):
            if not isinstance(artifact, dict):
                raise ValueError(f"Configured artifact {index} must be an object.")
            artifacts.append(
                {
                    "artifactType": artifact.get("artifactType", "text"),
                    "targetPath": artifact["targetPath"],
                    "content": artifact.get("content", ""),
                    "reason": artifact.get("reason", "Configured static provider artifact."),
                }
            )

        return {
            "manifestVersion": "1.0",
            "generationMode": "deterministic-provider-verification",
            "artifacts": artifacts,
            "notes": [
                "This manifest was produced by a local deterministic provider.",
                "It proves the AI Generation Engine boundary and staging workflow only.",
                "It must not be interpreted as real application CRUD generation.",
            ],
        }
