#!/usr/bin/env python3
"""Generate CCore backend CRUD files for pipelines."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.factory.crud.backend.generator_lib.backend_generator import BackendCrudGenerator
from scripts.factory.crud.backend.generator_lib.config_loader import load_json_config, resolve_repo_root

DEFAULT_CONFIG_PATH = SCRIPT_DIR / "config" / "generate_backend.json"


def generate_backend(config_path: Path) -> dict:
    config = load_json_config(config_path)
    repo_root = resolve_repo_root(config, config_path)
    generator = BackendCrudGenerator(script_directory=SCRIPT_DIR)
    return generator.generate(repo_root=repo_root, config=config)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CCore pipeline backend CRUD automation output.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to generate_backend.json")
    args = parser.parse_args()
    report = generate_backend(Path(args.config).resolve())
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()
