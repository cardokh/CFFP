from __future__ import annotations

import json
from pathlib import Path


def _cautomation_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "shared").is_dir())


def test_cautomation_reference_project_declares_project_and_module_contract_hierarchy():
    cautomation_root = _cautomation_root()
    project_root = cautomation_root / "projects/CAutomation"
    project_config = json.loads((project_root / "project.json").read_text(encoding="utf-8"))

    assert project_config["projectId"] == "CAutomation"
    assert project_config["contractHierarchy"]["projectLevel"] == "input/project/contracts"
    assert project_config["contractHierarchy"]["moduleLevel"] == "input/modules/{moduleId}/contracts"
    assert {module["moduleId"] for module in project_config["modules"]} == {
        "pipeline_management",
        "user_client_management",
    }
    assert (project_root / "input/project/contracts/client/Project_Client_Contract.pdf").exists()
    assert (project_root / "input/project/contracts/engineering/Project_Engineering_Contract.pdf").exists()
    assert (project_root / "input/modules/pipeline_management/contracts/Software_Requirements_Specification.pdf").exists()
    assert (project_root / "input/modules/pipeline_management/contracts/Architecture_and_Technical_Specification.pdf").exists()
    assert (project_root / "input/modules/user_client_management/contracts/Software_Requirements_Specification.md").exists()
    assert (project_root / "input/modules/user_client_management/contracts/Architecture_and_Technical_Specification.md").exists()
