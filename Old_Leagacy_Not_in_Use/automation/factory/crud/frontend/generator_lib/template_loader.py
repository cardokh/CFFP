"""Golden-template loading helpers."""
from __future__ import annotations

from pathlib import Path


class TemplateLoader:
    def __init__(self, repo_root: Path, golden_template: dict[str, str]) -> None:
        self.repo_root = repo_root
        self.golden_template = golden_template

    def read(self, key: str) -> str:
        relative_path = self.golden_template[key]
        template_path = self.repo_root / relative_path
        if not template_path.exists():
            raise FileNotFoundError(f"Golden template not found: {relative_path}")
        return template_path.read_text(encoding="utf-8")
