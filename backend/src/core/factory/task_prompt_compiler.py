"""Factory task prompt compiler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .task_context_collector import LocalTaskContextCollector
from .task_models import FactoryTask
from .task_prompt_models import CompiledTaskPrompt

DEFAULT_SYSTEM_INSTRUCTION = (
    "You are CCore Automation Factory. Follow the CCore engineering blueprint: "
    "no hardcoding, small files, thin services, dependency inversion, clear interfaces, "
    "and no infrastructure framework leakage into core."
)


@dataclass(frozen=True)
class FactoryTaskPromptCompiler:
    """Compiles repository context and task metadata into primitive prompt data."""

    project_root: Path
    context_collector: LocalTaskContextCollector

    def compile_prompt(self, task: FactoryTask, payload: dict[str, Any]) -> CompiledTaskPrompt:
        """Compile one Factory task into a prompt and system instruction."""

        context = self.context_collector.collect(payload)
        instruction = str(payload.get("instruction") or task.description or task.name).strip()
        system_instruction = str(payload.get("system_instruction") or DEFAULT_SYSTEM_INSTRUCTION).strip()
        prompt = "\n\n".join(
            (
                f"# Factory Task: {task.name}",
                f"Task ID: {task.task_id}",
                f"Task Definition: {task.task_definition_path}",
                "## Instruction",
                instruction,
                "## Repository Context",
                context.to_prompt_text(),
            )
        )
        return CompiledTaskPrompt(
            prompt=prompt,
            system_instruction=system_instruction,
            context_file_count=len(context.files),
        )


def build_default_task_prompt_compiler(project_root: Path) -> FactoryTaskPromptCompiler:
    """Build the default local prompt compiler."""

    return FactoryTaskPromptCompiler(
        project_root=project_root,
        context_collector=LocalTaskContextCollector(project_root=project_root),
    )
