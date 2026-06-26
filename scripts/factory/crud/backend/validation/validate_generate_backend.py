#!/usr/bin/env python3
"""Validate Backend CRUD Automation for pipeline generation."""
from __future__ import annotations

import argparse
import json
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.factory.crud.backend.generator_lib.config_loader import load_json_config, resolve_repo_root
from scripts.factory.crud.backend.generator_lib.report_writer import utc_timestamp, write_report
from scripts.factory.crud.backend.generate_backend import generate_backend

DEFAULT_CONFIG_PATH = SCRIPT_DIR / "config" / "validate_generate_backend.json"


def _copy_repo_without_heavy_dirs(repo_root: Path, target_root: Path) -> None:
    ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".venv", "node_modules")
    for item in repo_root.iterdir():
        target = target_root / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=ignore)
        else:
            shutil.copy2(item, target)


def _compile_python_files(paths: list[Path]) -> list[str]:
    compiled: list[str] = []
    for path in paths:
        py_compile.compile(str(path), doraise=True)
        compiled.append(str(path))
    return compiled


def validate_backend_generation(config_path: Path) -> dict[str, Any]:
    validation_config = load_json_config(config_path)
    repo_root = resolve_repo_root(validation_config, config_path)
    generation_config_path = repo_root / validation_config["generationConfigPath"]
    generation_config = load_json_config(generation_config_path)

    with tempfile.TemporaryDirectory(prefix="cffp_backend_generation_validate_") as temp_dir:
        temp_repo_root = Path(temp_dir) / "repo"
        temp_repo_root.mkdir(parents=True, exist_ok=True)
        _copy_repo_without_heavy_dirs(repo_root, temp_repo_root)

        temp_generation_config_path = temp_repo_root / validation_config["generationConfigPath"]
        temp_generation_config = load_json_config(temp_generation_config_path)
        temp_generation_config["repoRoot"] = str(temp_repo_root)
        temp_generation_config_path.write_text(json.dumps(temp_generation_config, indent=4), encoding="utf-8", newline="\n")

        generation_report = generate_backend(temp_generation_config_path)

        expected_output_dir = temp_repo_root / validation_config["expectedOutputPackageDirectory"]
        expected_files = [expected_output_dir / file_name for file_name in validation_config["expectedGeneratedFiles"]]
        missing_files = [str(path.relative_to(temp_repo_root)) for path in expected_files if not path.exists()]
        if missing_files:
            raise RuntimeError(f"Generated backend files missing: {missing_files}")

        patched_missing = [path for path in validation_config["expectedPatchedFiles"] if not (temp_repo_root / path).exists()]
        if patched_missing:
            raise RuntimeError(f"Expected patch target files missing: {patched_missing}")

        compiled_files = _compile_python_files([path for path in expected_files if path.suffix == ".py"])
        automation_python_files = list((temp_repo_root / "scripts/factory/crud/backend").rglob("*.py"))
        compiled_automation_files = _compile_python_files(automation_python_files)

    report = {
        "scriptName": "validate_generate_backend",
        "status": "passed",
        "validatedAt": utc_timestamp(),
        "entity": generation_config.get("entity"),
        "expectedGeneratedFiles": validation_config["expectedGeneratedFiles"],
        "compiledGeneratedFiles": compiled_files,
        "compiledAutomationFiles": compiled_automation_files,
        "generationReportStatus": generation_report.get("status"),
    }
    write_report(repo_root, validation_config.get("reportPath"), report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate CCore pipeline backend CRUD automation.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to validate_generate_backend.json")
    args = parser.parse_args()
    report = validate_backend_generation(Path(args.config).resolve())
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()
