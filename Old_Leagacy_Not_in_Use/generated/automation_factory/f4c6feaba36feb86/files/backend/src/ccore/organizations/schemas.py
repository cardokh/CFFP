from __future__ import annotations

from dataclasses import asdict

from .models import Organization


def organization_to_response(organization: Organization) -> dict:
    return asdict(organization)


def organization_collection_to_response(organizations: list[Organization]) -> dict:
    return {"items": [organization_to_response(item) for item in organizations]}
