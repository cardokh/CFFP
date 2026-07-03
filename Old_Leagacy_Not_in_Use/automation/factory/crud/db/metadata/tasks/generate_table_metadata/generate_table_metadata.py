"""Orchestrates the generate-table-metadata task."""

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

    db_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "run_db_tasks.py").is_file()
            and (parent / "metadata").is_dir()
            and (parent / "implementations").is_dir()
        ),
        None,
    )
    if db_root is not None and str(db_root) not in sys.path:
        sys.path.insert(0, str(db_root))


_configure_project_import_path()

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import print_passed
from support.db_path_utils import get_db_root
try:
    from .support.generate_generated_tables import generate_generated_tables
    from .support.import_generated_tables import import_generated_tables
except ImportError:  # Allows direct script execution from the task folder.
    from support.generate_generated_tables import generate_generated_tables
    from support.import_generated_tables import import_generated_tables


class GenerateTableMetadataScript(BaseScript):
    """Runs table-batch generation followed by deterministic metadata import."""

    def __init__(self) -> None:
        super().__init__(__file__)
        self.db_root = get_db_root(__file__)

    def run(self) -> None:
        started = time.perf_counter()

        print("Generating table metadata batches...")
        generation_result = generate_generated_tables(self.db_root, self.script_directory, self.config)

        print("Importing generated table metadata batches...")
        import_result = import_generated_tables(self.db_root, self.script_directory, self.config)

        report: dict[str, Any] = {
            "scriptName": self.script_name,
            "summary": {
                "status": "PASSED",
                "elapsedSeconds": round(time.perf_counter() - started, 3),
                "processedSpecificationCount": generation_result["processedSpecificationCount"],
                "generatedTableCount": generation_result["tableCount"],
                "importedTableCount": import_result["importedTableCount"],
            },
            "generation": generation_result,
            "import": import_result,
        }
        self.write_json_report(report)
        print_passed("generate_table_metadata")


if __name__ == "__main__":
    GenerateTableMetadataScript().run()
