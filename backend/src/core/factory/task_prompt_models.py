"""Factory task prompt compilation models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextFileSnapshot:
    """One text file included in a task context bundle."""

    path: str
    content: str
    truncated: bool = False


@dataclass(frozen=True)
class TaskContextBundle:
    """Collected context for one Factory task."""

    files: tuple[ContextFileSnapshot, ...]

    def to_prompt_text(self) -> str:
        """Render context as deterministic prompt text."""

        if not self.files:
            return "No repository context files were provided."

        sections: list[str] = []
        for file_snapshot in self.files:
            truncated_note = "\n[TRUNCATED]" if file_snapshot.truncated else ""
            sections.append(
                "\n".join(
                    (
                        f"## File: {file_snapshot.path}",
                        "```text",
                        file_snapshot.content,
                        "```",
                        truncated_note,
                    )
                ).strip()
            )
        return "\n\n".join(sections)


@dataclass(frozen=True)
class CompiledTaskPrompt:
    """Compiled primitive prompt data passed to execution providers."""

    prompt: str
    system_instruction: str | None
    context_file_count: int
