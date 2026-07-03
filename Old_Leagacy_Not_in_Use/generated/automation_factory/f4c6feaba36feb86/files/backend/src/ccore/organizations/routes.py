from __future__ import annotations

from .schemas import organization_collection_to_response, organization_to_response
from .services import OrganizationService

API_PATH_CCORE_ORGANIZATIONS = "/api/ccore/organizations"


def list_organizations(service: OrganizationService) -> dict:
    return organization_collection_to_response(service.list_organizations())


def get_organization(service: OrganizationService, organization_id: int) -> dict:
    organization = service.get_organization(organization_id)
    if organization is None:
        return {"error": "CCORE_ORGANIZATION_NOT_FOUND"}
    return organization_to_response(organization)
