"""Frontend CRUD generator orchestration."""
from __future__ import annotations

from pathlib import Path

from .config_loader import FrontendConfig
from .detail_templates import build_detail_html, build_detail_js
from .file_writer import write_text
from .frontend_artifacts import FrontendGenerationResult
from .frontend_wiring import add_api_endpoints, add_dashboard_card
from .golden_tasks_transformer import (
    build_list_css,
    build_list_html,
    build_list_js,
    read_golden_file,
)


class FrontendCrudGenerator:
    def __init__(self, repo_root: Path, config: FrontendConfig) -> None:
        self.repo_root = repo_root
        self.config = config
        self.written_files: list[str] = []
        self.unchanged_files: list[str] = []
        self.dashboard_updated = False
        self.api_endpoints_updated = False

    def generate(self) -> FrontendGenerationResult:
        self._validate_golden_template()
        self._generate_module_files()
        self._update_dashboard()
        self._update_api_endpoints()
        return FrontendGenerationResult(
            generated_entity=self.config.entity.name,
            written_files=self.written_files,
            unchanged_files=self.unchanged_files,
            dashboard_updated=self.dashboard_updated,
            api_endpoints_updated=self.api_endpoints_updated,
        )

    def _validate_golden_template(self) -> None:
        tasks_dir = self.repo_root / self.config.paths.tasks_module_dir
        required_files = [
            "tasks.html",
            "css/tasks.css",
            "js/tasks.js",
            "css/task-details.css",
        ]
        missing = [path for path in required_files if not (tasks_dir / path).is_file()]
        if missing:
            raise FileNotFoundError(f"Tasks golden template is incomplete: {', '.join(missing)}")

    def _record_write(self, relative_path: str, changed: bool) -> None:
        target = relative_path.replace("\\", "/")
        if changed:
            self.written_files.append(target)
        else:
            self.unchanged_files.append(target)

    def _write(self, relative_path: str, content: str) -> None:
        changed = write_text(self.repo_root / relative_path, content)
        self._record_write(relative_path, changed)

    def _generate_module_files(self) -> None:
        tasks_dir = self.repo_root / self.config.paths.tasks_module_dir
        out_dir = self.config.paths.output_module_dir.rstrip("/")
        entity = self.config.entity

        tasks_html = read_golden_file(tasks_dir, "tasks.html")
        tasks_css = read_golden_file(tasks_dir, "css/tasks.css")
        tasks_js = read_golden_file(tasks_dir, "js/tasks.js")
        details_css = read_golden_file(tasks_dir, "css/task-details.css")

        self._write(f"{out_dir}/pipelines.html", build_list_html(tasks_html, entity))
        self._write(f"{out_dir}/css/pipelines.css", build_list_css(tasks_css, entity))
        self._write(f"{out_dir}/js/pipelines.js", build_list_js(tasks_js, entity))
        self._write(f"{out_dir}/pipeline-details.html", build_detail_html(entity))
        self._write(f"{out_dir}/css/pipeline-details.css", build_list_css(details_css, entity) + "\n\n.ccore-pipeline-description-field {\n    margin-top: 1rem;\n}\n\n.ccore-pipeline-description-field textarea {\n    min-height: 7rem;\n    resize: vertical;\n}\n")
        self._write(f"{out_dir}/js/pipeline-details.js", build_detail_js(entity))

    def _update_dashboard(self) -> None:
        relative_path = self.config.paths.automation_dashboard
        path = self.repo_root / relative_path
        updated, changed = add_dashboard_card(path.read_text(encoding="utf-8"))
        self.dashboard_updated = changed
        self._write(relative_path, updated)

    def _update_api_endpoints(self) -> None:
        relative_path = self.config.paths.api_endpoints
        path = self.repo_root / relative_path
        updated, changed = add_api_endpoints(path.read_text(encoding="utf-8"), self.config.entity)
        self.api_endpoints_updated = changed
        self._write(relative_path, updated)
