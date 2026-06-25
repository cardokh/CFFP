from __future__ import annotations

import json
import os
import re
from typing import Any

from scripts.factory.ai_generation_engine.ai_generation_contracts import (
    LlmGenerationOptions,
    LlmGenerationResult,
)


class GeminiProvider:
    """
    Google Gemini adapter for the CFFP AI Generation Engine.

    This provider is a strict translation adapter. It keeps all Gemini SDK usage
    inside the provider boundary and returns the same JSON artifact manifest
    contract consumed by AiGenerationEngine.
    """

    provider_id = "gemini-provider"

    _ABORT_FINISH_REASONS = {"MAX_TOKENS", "INCOMPLETE"}
    _SUCCESS_FINISH_REASONS = {"STOP"}

    def generate(
        self,
        *,
        prompt: str,
        options: LlmGenerationOptions,
    ) -> LlmGenerationResult:
        api_key = self._read_api_key()
        genai, types = self._load_google_genai_sdk()

        model_name = self._resolve_model_name(options)
        temperature = self._resolve_temperature(options)
        max_output_tokens = self._resolve_max_output_tokens(options)

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self._generation_response_schema(),
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_instruction=self._system_instruction(options),
        )

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )

        finish_reason = self._extract_finish_reason(response)
        self._assert_complete_finish(finish_reason)

        response_text = self._extract_response_text(response)
        manifest = self._parse_structured_response(response, response_text)
        normalized_response_text = self._to_normalized_json(manifest)

        return LlmGenerationResult(
            provider_id=self.provider_id,
            model_metadata={
                "model": model_name,
                "vendor": "google",
                "adapter": "gemini-structured-output",
                "responseSchema": "c_ffp_generation_response_v1",
            },
            response_text=normalized_response_text,
            finish_reason=finish_reason,
            usage_metadata=self._extract_usage_metadata(
                response=response,
                prompt=prompt,
                raw_response_text=response_text,
            ),
        )

    def _read_api_key(self) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required for GeminiProvider.")
        return api_key

    def _load_google_genai_sdk(self) -> tuple[Any, Any]:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ImportError(
                "GeminiProvider requires the google-genai package. "
                "Install project dependencies before using provider=gemini."
            ) from exc
        return genai, types

    def _resolve_model_name(self, options: LlmGenerationOptions) -> str:
        configured_model = options.model or options.extra.get("modelName")
        if isinstance(configured_model, str) and configured_model.strip():
            return configured_model.strip()
        return "gemini-2.5-pro"

    def _resolve_temperature(self, options: LlmGenerationOptions) -> float:
        if options.temperature is None:
            return 0.0
        return float(options.temperature)

    def _resolve_max_output_tokens(self, options: LlmGenerationOptions) -> int | None:
        if options.max_output_tokens is None:
            extra_value = options.extra.get("maxOutputTokens")
            if extra_value is None:
                return None
            return int(extra_value)
        return int(options.max_output_tokens)

    def _system_instruction(self, options: LlmGenerationOptions) -> str:
        configured_instruction = options.extra.get("systemInstruction")
        if isinstance(configured_instruction, str) and configured_instruction.strip():
            return configured_instruction.strip()

        return "\n".join(
            [
                "You are the CFFP Automation Factory code generation provider.",
                "Return only structured JSON matching the configured response schema.",
                "Do not return markdown fences, conversational commentary, or explanatory text outside JSON.",
                "Generate whole-file contents only. Do not provide snippets or placeholders.",
                "Every artifact targetPath must be repository-relative and must not contain path traversal.",
                "If the requested generation cannot be completed safely, return an empty artifacts array with a note.",
            ]
        )

    def _generation_response_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "manifestVersion": {
                    "type": "string",
                    "description": "Artifact manifest contract version.",
                },
                "generationMode": {
                    "type": "string",
                    "description": "Provider generation mode or strategy.",
                },
                "artifacts": {
                    "type": "array",
                    "description": "Whole-file generated artifacts for staging.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "artifactType": {
                                "type": "string",
                                "description": "Artifact classification such as backend, frontend, database, test, or config.",
                            },
                            "targetPath": {
                                "type": "string",
                                "description": "Repository-relative target path for the generated whole-file artifact.",
                            },
                            "content": {
                                "type": "string",
                                "description": "Complete generated source file contents. No snippets, omissions, or placeholders.",
                            },
                            "reason": {
                                "type": "string",
                                "description": "Architectural reason for generating this artifact.",
                            },
                        },
                        "required": ["artifactType", "targetPath", "content", "reason"],
                    },
                },
                "notes": {
                    "type": "array",
                    "description": "Optional provider notes about safe generation decisions.",
                    "items": {"type": "string"},
                },
            },
            "required": ["manifestVersion", "artifacts"],
        }

    def _extract_finish_reason(self, response: Any) -> str:
        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            return "NO_CANDIDATES"

        finish_reason = getattr(candidates[0], "finish_reason", None)
        if finish_reason is None:
            return "UNKNOWN"

        name = getattr(finish_reason, "name", None)
        if isinstance(name, str) and name:
            return name
        return str(finish_reason)

    def _assert_complete_finish(self, finish_reason: str) -> None:
        normalized = finish_reason.upper()
        if normalized in self._ABORT_FINISH_REASONS:
            raise ValueError(
                "AI generation aborted early by provider. "
                f"Reason: {finish_reason}. Output limit exceeded or response incomplete."
            )
        if normalized not in self._SUCCESS_FINISH_REASONS:
            raise ValueError(f"AI generation did not complete successfully. Provider finish reason: {finish_reason}.")

    def _extract_response_text(self, response: Any) -> str:
        response_text = getattr(response, "text", None)
        if isinstance(response_text, str) and response_text.strip():
            return response_text.strip()
        raise ValueError("GeminiProvider response did not include non-empty JSON text.")

    def _parse_structured_response(self, response: Any, response_text: str) -> dict[str, Any]:
        parsed_response = getattr(response, "parsed", None)
        if parsed_response is not None:
            manifest = self._coerce_parsed_response(parsed_response)
            return self._validate_manifest(manifest)

        try:
            manifest = json.loads(response_text)
        except json.JSONDecodeError:
            manifest = self._parse_markdown_json_fallback(response_text)
        return self._validate_manifest(manifest)

    def _coerce_parsed_response(self, parsed_response: Any) -> dict[str, Any]:
        if isinstance(parsed_response, dict):
            return dict(parsed_response)
        model_dump = getattr(parsed_response, "model_dump", None)
        if callable(model_dump):
            return dict(model_dump(by_alias=True))
        to_dict = getattr(parsed_response, "to_dict", None)
        if callable(to_dict):
            return dict(to_dict())
        raise ValueError("GeminiProvider parsed response could not be converted to a manifest object.")

    def _parse_markdown_json_fallback(self, response_text: str) -> dict[str, Any]:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, flags=re.DOTALL | re.IGNORECASE)
        if not match:
            raise ValueError("GeminiProvider response was neither structured JSON nor a JSON markdown fallback block.")
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            raise ValueError("GeminiProvider JSON markdown fallback block was malformed.") from exc

    def _validate_manifest(self, manifest: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(manifest, dict):
            raise ValueError("GeminiProvider manifest root must be an object.")

        artifacts = manifest.get("artifacts")
        if artifacts is None:
            manifest["artifacts"] = []
        elif not isinstance(artifacts, list):
            raise ValueError("GeminiProvider manifest field artifacts must be a list.")

        for index, artifact in enumerate(manifest["artifacts"], start=1):
            self._validate_artifact(artifact, index)

        if not isinstance(manifest.get("manifestVersion"), str) or not manifest["manifestVersion"].strip():
            manifest["manifestVersion"] = "1.0"
        return manifest

    def _validate_artifact(self, artifact: Any, index: int) -> None:
        if not isinstance(artifact, dict):
            raise ValueError(f"GeminiProvider artifact {index} must be an object.")

        for field_name in ["artifactType", "targetPath", "content", "reason"]:
            if field_name not in artifact:
                raise ValueError(f"GeminiProvider artifact {index} missing required field: {field_name}.")
            if not isinstance(artifact[field_name], str):
                raise ValueError(f"GeminiProvider artifact {index} field {field_name} must be a string.")

    def _to_normalized_json(self, manifest: dict[str, Any]) -> str:
        return json.dumps(manifest, indent=4, sort_keys=True)

    def _extract_usage_metadata(self, *, response: Any, prompt: str, raw_response_text: str) -> dict[str, Any]:
        usage = getattr(response, "usage_metadata", None)
        usage_dict: dict[str, Any] = {}
        if usage is not None:
            to_dict = getattr(usage, "to_dict", None)
            if callable(to_dict):
                usage_dict.update(to_dict())
            else:
                model_dump = getattr(usage, "model_dump", None)
                if callable(model_dump):
                    usage_dict.update(model_dump())

        usage_dict.update(
            {
                "promptCharacters": len(prompt),
                "rawResponseCharacters": len(raw_response_text),
            }
        )
        return usage_dict
