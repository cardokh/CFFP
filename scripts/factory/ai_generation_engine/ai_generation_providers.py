from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from scripts.factory.ai_generation_engine.ai_generation_contracts import (
    LlmGenerationResponse,
    PromptMetadata,
)


class LocalDeterministicManifestProvider:
    """
    Local provider used to validate the AI Generation Engine without coupling the
    engine to Gemini, OpenAI, or any specific external vendor.

    The provider consumes the assembled prompt and returns a complete artifact
    manifest in the same shape an external provider must return later.
    """

    provider_id = "local-deterministic-manifest-provider"

    def generate(
        self,
        *,
        prompt: str,
        prompt_metadata: PromptMetadata,
        provider_config: dict,
    ) -> LlmGenerationResponse:
        target_entity = provider_config.get("targetEntity", "Organization")
        module_slug = provider_config.get("moduleSlug", "organizations")
        api_prefix = provider_config.get("apiPrefix", "/api/ccore/organizations")
        artifact_manifest = self._build_manifest(
            target_entity=target_entity,
            module_slug=module_slug,
            api_prefix=api_prefix,
            prompt_metadata=prompt_metadata,
            provider_config=provider_config,
        )
        response_text = json.dumps(
            artifact_manifest,
            indent=4,
            sort_keys=True,
        )

        return LlmGenerationResponse(
            provider_id=self.provider_id,
            model_metadata={
                "providerType": "local",
                "modelName": provider_config.get("modelName", "deterministic-artifact-manifest-v1"),
                "modelVersion": provider_config.get("modelVersion", "1.0"),
                "vendor": "none",
                "executionMode": "deterministic-local",
            },
            response_text=response_text,
            response_sha256=_sha256(response_text),
            finish_reason="completed",
            usage_metadata={
                "promptCharacterCount": len(prompt),
                "promptLineCount": _line_count(prompt),
                "responseCharacterCount": len(response_text),
                "responseLineCount": _line_count(response_text),
                "tokenCountAvailable": False,
            },
        )

    def _build_manifest(
        self,
        *,
        target_entity: str,
        module_slug: str,
        api_prefix: str,
        prompt_metadata: PromptMetadata,
        provider_config: dict,
    ) -> dict:
        source_reference = prompt_metadata.source_path
        artifact_generation_timestamp = provider_config.get(
            "artifactGenerationTimestamp",
            "deterministic-local-execution",
        )

        artifacts = [
            _artifact(
                artifact_type="backend_package_init",
                target_path=f"backend/src/ccore/{module_slug}/__init__.py",
                content='"""Generated CCore Organization CRUD module."""\n',
                reason="Create package marker for the generated Organization module.",
                source_reference=source_reference,
            ),
            _artifact(
                artifact_type="backend_model",
                target_path=f"backend/src/ccore/{module_slug}/models.py",
                content=_models_py(),
                reason="Create provider-generated Organization domain model in staging.",
                source_reference=source_reference,
            ),
            _artifact(
                artifact_type="backend_schemas",
                target_path=f"backend/src/ccore/{module_slug}/schemas.py",
                content=_schemas_py(),
                reason="Create provider-generated request/response schema helpers in staging.",
                source_reference=source_reference,
            ),
            _artifact(
                artifact_type="backend_repository",
                target_path=f"backend/src/ccore/{module_slug}/repositories.py",
                content=_repositories_py(),
                reason="Create provider-generated repository contract and in-memory implementation in staging.",
                source_reference=source_reference,
            ),
            _artifact(
                artifact_type="backend_service",
                target_path=f"backend/src/ccore/{module_slug}/services.py",
                content=_services_py(),
                reason="Create provider-generated service layer in staging.",
                source_reference=source_reference,
            ),
            _artifact(
                artifact_type="backend_api_routes",
                target_path=f"backend/src/ccore/{module_slug}/routes.py",
                content=_routes_py(api_prefix),
                reason="Create provider-generated route declarations in staging.",
                source_reference=source_reference,
            ),
            _artifact(
                artifact_type="frontend_list_page",
                target_path="frontend/static/desktop/protected/ccore/organizations.html",
                content=_organizations_html(),
                reason="Create staged list page for Organization CRUD.",
                source_reference=source_reference,
            ),
            _artifact(
                artifact_type="frontend_list_js",
                target_path="frontend/static/desktop/protected/ccore/js/organizations.js",
                content=_organizations_js(api_prefix),
                reason="Create staged list-page script for Organization CRUD.",
                source_reference=source_reference,
            ),
            _artifact(
                artifact_type="frontend_css",
                target_path="frontend/static/desktop/protected/ccore/css/organizations.css",
                content=_organizations_css(),
                reason="Create staged list-page styling for Organization CRUD.",
                source_reference=source_reference,
            ),
        ]

        return {
            "manifestVersion": "1.0",
            "generationRequest": {
                "taskName": "Generate CRUD Module",
                "targetEntity": target_entity,
                "sourceSpecification": source_reference,
                "goldenReference": [
                    "compiled into master-context.md",
                ],
            },
            "technologyStack": {
                "database": "PostgreSQL-compatible configuration staged later by validation/apply pipeline",
                "backend": "Python standard library route-compatible staged artifacts",
                "frontend": "Static HTML/CSS/JavaScript",
                "orchestration": "CFFP Automation Factory",
                "aiProvider": self.provider_id,
                "aiModel": provider_config.get("modelName", "deterministic-artifact-manifest-v1"),
            },
            "artifacts": artifacts,
            "requiredManualDecisions": [],
            "validationHints": [
                "Stage artifacts only; do not apply to production source in Iteration 2.",
                "Compile staged Python files before validation/apply iteration.",
            ],
            "generationNotes": [
                "Manifest generated by replaceable local provider for Iteration 2 engine validation.",
                f"Artifact generation timestamp: {artifact_generation_timestamp}",
            ],
        }


def _artifact(
    *,
    artifact_type: str,
    target_path: str,
    content: str,
    reason: str,
    source_reference: str,
) -> dict:
    return {
        "artifactType": artifact_type,
        "targetPath": target_path,
        "changeType": "create",
        "contentEncoding": "utf-8",
        "content": content,
        "reason": reason,
        "sourceReference": source_reference,
    }


def _models_py() -> str:
    return '''from __future__ import annotations\n\nfrom dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass Organization:\n    organization_id: int\n    organization_type_id: int\n    organization_name: str\n    organization_code: str\n    description: str | None\n    is_active: bool\n    created_at: str | None = None\n    updated_at: str | None = None\n'''


def _schemas_py() -> str:
    return '''from __future__ import annotations\n\nfrom dataclasses import asdict\n\nfrom .models import Organization\n\n\ndef organization_to_response(organization: Organization) -> dict:\n    return asdict(organization)\n\n\ndef organization_collection_to_response(organizations: list[Organization]) -> dict:\n    return {"items": [organization_to_response(item) for item in organizations]}\n'''


def _repositories_py() -> str:
    return '''from __future__ import annotations\n\nfrom typing import Protocol\n\nfrom .models import Organization\n\n\nclass OrganizationRepository(Protocol):\n    def list_organizations(self) -> list[Organization]:\n        ...\n\n    def get_organization(self, organization_id: int) -> Organization | None:\n        ...\n\n\nclass InMemoryOrganizationRepository:\n    def __init__(self, organizations: list[Organization] | None = None):\n        self._organizations = organizations or []\n\n    def list_organizations(self) -> list[Organization]:\n        return list(self._organizations)\n\n    def get_organization(self, organization_id: int) -> Organization | None:\n        for organization in self._organizations:\n            if organization.organization_id == organization_id:\n                return organization\n        return None\n'''


def _services_py() -> str:
    return '''from __future__ import annotations\n\nfrom .models import Organization\nfrom .repositories import OrganizationRepository\n\n\nclass OrganizationService:\n    def __init__(self, repository: OrganizationRepository):\n        self._repository = repository\n\n    def list_organizations(self) -> list[Organization]:\n        return self._repository.list_organizations()\n\n    def get_organization(self, organization_id: int) -> Organization | None:\n        return self._repository.get_organization(organization_id)\n'''


def _routes_py(api_prefix: str) -> str:
    return f'''from __future__ import annotations\n\nfrom .schemas import organization_collection_to_response, organization_to_response\nfrom .services import OrganizationService\n\nAPI_PATH_CCORE_ORGANIZATIONS = "{api_prefix}"\n\n\ndef list_organizations(service: OrganizationService) -> dict:\n    return organization_collection_to_response(service.list_organizations())\n\n\ndef get_organization(service: OrganizationService, organization_id: int) -> dict:\n    organization = service.get_organization(organization_id)\n    if organization is None:\n        return {{"error": "CCORE_ORGANIZATION_NOT_FOUND"}}\n    return organization_to_response(organization)\n'''


def _organizations_html() -> str:
    return '''<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>CCore Organizations</title>\n    <link rel="stylesheet" href="./css/organizations.css">\n</head>\n<body>\n    <main class="ccore-organizations-page">\n        <header>\n            <h1>CCore Organizations</h1>\n            <p>Manage CCore organizations.</p>\n        </header>\n        <section id="organizations-status" aria-live="polite">Loading organizations...</section>\n        <table id="organizations-table">\n            <thead>\n                <tr>\n                    <th>Name</th>\n                    <th>Code</th>\n                    <th>Type</th>\n                    <th>Active</th>\n                    <th>Updated</th>\n                </tr>\n            </thead>\n            <tbody></tbody>\n        </table>\n    </main>\n    <script src="./js/organizations.js"></script>\n</body>\n</html>\n'''


def _organizations_js(api_prefix: str) -> str:
    return f'''const ORGANIZATIONS_ENDPOINT = "{api_prefix}";\n\nasync function loadOrganizations() {{\n    const statusElement = document.getElementById("organizations-status");\n    const tableBody = document.querySelector("#organizations-table tbody");\n\n    try {{\n        const response = await fetch(ORGANIZATIONS_ENDPOINT);\n        const payload = await response.json();\n        const items = payload.items || [];\n\n        tableBody.innerHTML = items.map((organization) => `\n            <tr data-organization-id="${{organization.organization_id}}">\n                <td>${{organization.organization_name || ""}}</td>\n                <td>${{organization.organization_code || ""}}</td>\n                <td>${{organization.organization_type_name || ""}}</td>\n                <td>${{organization.is_active ? "Yes" : "No"}}</td>\n                <td>${{organization.updated_at || ""}}</td>\n            </tr>\n        `).join("");\n\n        statusElement.textContent = `${{items.length}} organization(s) loaded.`;\n    }} catch (error) {{\n        statusElement.textContent = "Could not load organizations.";\n    }}\n}}\n\ndocument.addEventListener("DOMContentLoaded", loadOrganizations);\n'''


def _organizations_css() -> str:
    return '''.ccore-organizations-page {\n    max-width: 1100px;\n    margin: 0 auto;\n    padding: 24px;\n}\n\n#organizations-table {\n    width: 100%;\n    border-collapse: collapse;\n}\n\n#organizations-table th,\n#organizations-table td {\n    padding: 8px 10px;\n    text-align: left;\n    border-bottom: 1px solid #ddd;\n}\n'''


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _line_count(content: str) -> int:
    if content == "":
        return 0
    return content.count("\n") + (0 if content.endswith("\n") else 1)
