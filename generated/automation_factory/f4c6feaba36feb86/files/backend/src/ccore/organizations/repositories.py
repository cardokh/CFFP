from __future__ import annotations

from typing import Protocol

from .models import Organization


class OrganizationRepository(Protocol):
    def list_organizations(self) -> list[Organization]:
        ...

    def get_organization(self, organization_id: int) -> Organization | None:
        ...


class InMemoryOrganizationRepository:
    def __init__(self, organizations: list[Organization] | None = None):
        self._organizations = organizations or []

    def list_organizations(self) -> list[Organization]:
        return list(self._organizations)

    def get_organization(self, organization_id: int) -> Organization | None:
        for organization in self._organizations:
            if organization.organization_id == organization_id:
                return organization
        return None
