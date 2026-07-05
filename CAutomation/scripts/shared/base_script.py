from datetime import datetime
from pathlib import Path

from scripts.shared.script_config_utils import (
    load_config,
)
from scripts.shared.script_json_utils import (
    write_json_file,
)
from scripts.shared.script_path_utils import (
    get_project_root,
    to_relative_path,
)


class BaseScript:
    """
    Shared reusable base class for project scripts.
    """

    def __init__(self, script_file: str):
        self.script_path = Path(script_file).resolve()
        self.script_directory = self.script_path.parent
        self.script_name = self.script_path.stem

        self.config_directory = self.script_directory / "config"
        self.output_directory = self.script_directory / "output"
        self.config_path = self.config_directory / f"{self.script_name}.json"

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.project_root = get_project_root()

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.config = load_config(
            self.config_path,
        )

    def get_output_file_path(
        self,
        suffix: str = "json",
    ) -> Path:
        return self.output_directory / f"{self.script_name}_{self.timestamp}.{suffix}"

    def write_json_report(
        self,
        report: dict,
    ) -> Path:
        report_path = self.get_output_file_path("json")

        write_json_file(
            report_path,
            report,
        )

        return report_path

    def to_project_relative_path(
        self,
        path: Path,
    ) -> str:
        return to_relative_path(
            self.project_root,
            path,
        )
