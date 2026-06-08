from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_json_utils import (
    write_json_file,
)


class CreateBlueprintJsonFiles(BaseScript):
    def __init__(self):
        super().__init__(__file__)

    def get_target_folder(self) -> str:
        target_folder = self.config.get("targetFolder")

        if not isinstance(
            target_folder,
            str,
        ):
            raise ValueError("Config must contain 'targetFolder'.")

        return target_folder

    def get_file_names(self) -> list[str]:
        file_names = self.config.get("files")

        if not isinstance(
            file_names,
            list,
        ):
            raise ValueError("Config must contain 'files'.")

        for file_name in file_names:
            if not isinstance(
                file_name,
                str,
            ):
                raise ValueError("Every file name must be a string.")

        return file_names

    def build_rule_file_content(
        self,
        file_name: str,
    ) -> dict:
        rule_set_name = file_name.replace(
            ".json",
            "",
        )

        return {
            "ruleSetName": rule_set_name,
            "description": "",
            "rules": [],
        }

    def run(self) -> None:
        target_folder = self.project_root / self.get_target_folder()

        target_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        created_count = 0
        skipped_count = 0

        for file_name in self.get_file_names():
            file_path = target_folder / file_name

            if file_path.exists():
                skipped_count += 1
                continue

            write_json_file(
                file_path,
                self.build_rule_file_content(file_name),
            )

            created_count += 1

        print_passed(
            (
                "Blueprint JSON files created. "
                f"Created: {created_count}. "
                f"Skipped existing: {skipped_count}. "
                "Target folder: "
                f"{self.to_project_relative_path(target_folder)}"
            )
        )


def main() -> None:
    try:
        CreateBlueprintJsonFiles().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()
