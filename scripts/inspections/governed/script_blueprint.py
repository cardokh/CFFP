from pathlib import Path

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_json_utils import (
    write_json_file,
)


class ScriptBlueprint(BaseScript):
    def __init__(self):
        super().__init__(__file__)

    def get_output_file_name(self) -> str:
        output_file_name = self.config.get("outputFileName")

        if not isinstance(
            output_file_name,
            str,
        ):
            raise ValueError("Config must contain 'outputFileName'.")

        return output_file_name

    def run(self) -> None:
        blueprint_report = self._build_blueprint_report()
        output_file_path = self._write_blueprint_report(blueprint_report)

        self._print_success(output_file_path)

    def _build_blueprint_report(self) -> dict:
        return self.config

    def _write_blueprint_report(
        self,
        blueprint_report: dict,
    ) -> Path:
        output_file_path = self.output_directory / self.get_output_file_name()

        write_json_file(
            output_file_path,
            blueprint_report,
        )

        return output_file_path

    def _print_success(
        self,
        output_file_path: Path,
    ) -> None:
        print_passed(
            (
                "Script blueprint completed. "
                "Config written to: "
                f"{self.to_project_relative_path(output_file_path)}"
            )
        )


def main() -> None:
    try:
        ScriptBlueprint().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
