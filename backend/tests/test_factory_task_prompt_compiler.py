"""Factory task prompt compiler tests."""

from __future__ import annotations

from pathlib import Path

from src.core.factory.task_models import FactoryTask
from src.core.factory.task_prompt_compiler import build_default_task_prompt_compiler
from src.core.factory.task_status import TASK_STATUS_PENDING


def test_prompt_compiler_collects_payload_context(tmp_path: Path) -> None:
    target_file = tmp_path / "sample.txt"
    target_file.write_text("sample context", encoding="utf-8")
    task = FactoryTask(
        task_id="factory.prompt",
        name="Prompt Task",
        description="Compile a prompt.",
        status=TASK_STATUS_PENDING,
        task_definition_path="tasks/prompt.json",
        priority=10,
    )

    compiled_prompt = build_default_task_prompt_compiler(tmp_path).compile_prompt(
        task,
        {
            "instruction": "Use the context.",
            "context_targets": ["sample.txt"],
        },
    )

    assert compiled_prompt.context_file_count == 1
    assert "Use the context." in compiled_prompt.prompt
    assert "sample context" in compiled_prompt.prompt
    assert compiled_prompt.system_instruction is not None
