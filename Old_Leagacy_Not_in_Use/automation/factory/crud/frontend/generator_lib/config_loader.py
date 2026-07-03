"""Configuration loading for frontend CRUD generation."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EntityConfig:
    name: str
    plural_name: str
    api_key: str
    api_list_property: str
    api_detail_property: str
    id_field: str
    name_field: str
    description_field: str
    status_id_field: str
    status_label_field: str
    created_at_field: str
    api_base_path: str
    api_status_path: str
    status_response_property: str
    table_name: str


@dataclass(frozen=True)
class PathConfig:
    tasks_module_dir: str
    automation_dashboard: str
    api_endpoints: str
    output_module_dir: str
    report: str


@dataclass(frozen=True)
class FrontendConfig:
    entity: EntityConfig
    paths: PathConfig


def load_config(config_path: Path) -> FrontendConfig:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return FrontendConfig(
        entity=EntityConfig(**data["entity"]),
        paths=PathConfig(**data["paths"]),
    )
