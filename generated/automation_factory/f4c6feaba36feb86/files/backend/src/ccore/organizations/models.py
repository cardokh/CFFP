from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Organization:
    organization_id: int
    organization_type_id: int
    organization_name: str
    organization_code: str
    description: str | None
    is_active: bool
    created_at: str | None = None
    updated_at: str | None = None
