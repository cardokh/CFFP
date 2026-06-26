"""File writing helpers for backend CRUD automation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileWriteResult:
    path: str
    status: str


def write_text_file(repo_root: Path, relative_path: str, content: str, overwrite: bool) -> FileWriteResult:
    target_path = repo_root / relative_path
    if target_path.exists() and not overwrite:
        return FileWriteResult(path=relative_path, status="skipped")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding="utf-8", newline="\n")
    return FileWriteResult(path=relative_path, status="written")


def ensure_init_file(repo_root: Path, relative_directory: str, overwrite: bool = False) -> FileWriteResult:
    return write_text_file(
        repo_root=repo_root,
        relative_path=f"{relative_directory.rstrip('/')}/__init__.py",
        content='"""Generated backend CRUD package."""\n',
        overwrite=overwrite,
    )
