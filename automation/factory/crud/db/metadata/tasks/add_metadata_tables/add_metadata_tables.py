"""Orchestrates the add-metadata-tables task."""

import sys
import time
from pathlib import Path
from typing import Any


def _configure_project_import_path() -> None:
    project_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "shared").is_dir()
        ),
        None,
    )
    if project_root is None:
        raise RuntimeError("Could not locate project root containing scripts/shared.")
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_passed
try:
    from .support.generate_generated_tables import generate_generated_tables
    from .support.import_generated_tables import import_generated_tables
except ImportError:  # Allows direct script execution from the task folder.
    from support.generate_generated_tables import generate_generated_tables
    from support.import_generated_tables import import_generated_tables


class AddMetadataTablesScript(BaseScript):
    """Runs table-batch generation followed by deterministic metadata import."""

    def __init__(self) -> None:
        super().__init__(__file__)

    def run(self) -> None:
        started = time.perf_counter()

        print("Generating table batch...")
        generation_result = generate_generated_tables(self.script_directory, self.config)

        print("Importing generated table batch...")
        import_result = import_generated_tables(self.project_root, self.script_directory, self.config)

        report: dict[str, Any] = {
            "scriptName": self.script_name,
            "summary": {
                "status": "PASSED",
                "elapsedSeconds": round(time.perf_counter() - started, 3),
                "generatedTableCount": generation_result["tableCount"],
                "importedTableCount": import_result["importedTableCount"],
            },
            "generation": generation_result,
            "import": import_result,
        }
        self.write_json_report(report)
        print_passed("add_metadata_tables")


if __name__ == "__main__":
    AddMetadataTablesScript().run()
