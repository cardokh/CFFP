"""Template loading for backend CRUD automation."""
from __future__ import annotations

from pathlib import Path


class BackendTemplateRegistry:
    def __init__(self, template_directory: Path):
        self.template_directory = template_directory

    def load_template(self, template_name: str) -> str:
        template_path = self.template_directory / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Backend template not found: {template_path}")
        return template_path.read_text(encoding="utf-8")
