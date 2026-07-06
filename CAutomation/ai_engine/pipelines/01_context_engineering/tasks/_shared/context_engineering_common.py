"""Shared helpers for Pipeline 01 - Context Engineering tasks."""

from __future__ import annotations

import sys
from pathlib import Path


_PROJECT_ROOT = next(
    (parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir()),
    None,
)
if _PROJECT_ROOT is not None:
    # Tasks import shared scripts as scripts.shared.* and runtime modules as
    # CAutomation.ai_engine.*. Both the CAutomation root and its parent must
    # be importable when tasks are executed directly from the repository root.
    for import_root in (_PROJECT_ROOT, _PROJECT_ROOT.parent):
        if str(import_root) not in sys.path:
            sys.path.insert(0, str(import_root))

from CAutomation.ai_engine.runtime.task_runtime import (  # noqa: E402
    RuntimeTaskSupportMixin,
    clean_directory,
    configure_project_import_path,
    source_record,
    utc_now_iso,
)



class ContextEngineeringSupportMixin(RuntimeTaskSupportMixin):
    """Pipeline 01 specific runtime support."""

    def contract_paths(self) -> tuple[Path, Path]:
        input_config = self.group("input")
        module_root = self.module_input_root()
        return module_root / input_config["srsFileName"], module_root / input_config["atsFileName"]

    def project_client_input_root(self) -> Path:
        input_config = self.group("input")
        configured_path = input_config.get("projectClientInputPath", "projects/{projectId}/input/client")
        return (self.CAutomation_root() / self.resolve_placeholders(str(configured_path))).resolve()

    def project_engineering_input_root(self) -> Path:
        input_config = self.group("input")
        configured_path = input_config.get("projectEngineeringInputPath", "projects/{projectId}/input/engineering")
        return (self.CAutomation_root() / self.resolve_placeholders(str(configured_path))).resolve()

    def document_source_root(self, source_root: str) -> Path:
        normalized = source_root.strip().lower()
        if normalized == "project_client":
            return self.project_client_input_root()
        if normalized == "project_engineering":
            return self.project_engineering_input_root()
        if normalized == "module":
            return self.module_input_root()
        raise ValueError(f"Unsupported document source root: {source_root}")

    def normalized_input_root(self) -> Path:
        input_config = self.group("input")
        configured_path = input_config.get("normalizedInputPath", "projects/{projectId}/normalized_input")
        return (self.CAutomation_root() / self.resolve_placeholders(str(configured_path))).resolve()

    def normalized_project_input_root(self) -> Path:
        input_config = self.group("input")
        configured_path = input_config.get("normalizedProjectInputPath", "projects/{projectId}/normalized_input/project/contracts")
        return (self.CAutomation_root() / self.resolve_placeholders(str(configured_path))).resolve()

    def normalized_module_input_root(self) -> Path:
        input_config = self.group("input")
        configured_path = input_config.get("normalizedModuleInputPath", "projects/{projectId}/normalized_input/modules/{moduleId}/contracts")
        return (self.CAutomation_root() / self.resolve_placeholders(str(configured_path))).resolve()

    def context_package_dir(self) -> Path:
        output_config = self.group("output")
        package_root = self.CAutomation_root() / self.resolve_placeholders(output_config["contextPackageRoot"])
        package_id = self.resolve_placeholders(output_config["contextPackageId"])
        return (package_root / package_id).resolve()
