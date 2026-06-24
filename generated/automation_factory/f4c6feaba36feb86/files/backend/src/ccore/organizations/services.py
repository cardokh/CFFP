from __future__ import annotations

from .models import Organization
from .repositories import OrganizationRepository


class OrganizationService:
    def __init__(self, repository: OrganizationRepository):
        self._repository = repository

    def list_organizations(self) -> list[Organization]:
        return self._repository.list_organizations()

    def get_organization(self, organization_id: int) -> Organization | None:
        return self._repository.get_organization(organization_id)
