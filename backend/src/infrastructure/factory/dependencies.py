"""Factory infrastructure composition root.

This module is intentionally outside src.core. It wires concrete infrastructure
adapters to core interfaces and returns ready-to-use core use cases.
"""

from __future__ import annotations

from pathlib import Path

from src.core.factory.interfaces.task_repository import ITaskRepository
from src.core.factory.task_prompt_compiler import build_default_task_prompt_compiler
from src.core.factory.task_runner import FactoryTaskRunner
from src.core.infrastructure.database import DatabaseManager
from src.infrastructure.ai.dependencies import build_llm_provider
from src.infrastructure.orchestration.prefect.prefect_execution_provider import (
    PrefectExecutionProvider,
)
from src.infrastructure.persistence.sqlite.factory.sql_task_repository import SqlTaskRepository


def build_sql_task_repository(database_path: Path) -> ITaskRepository:
    """Build the SQL-backed Factory task repository adapter."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    return SqlTaskRepository(DatabaseManager(str(database_path)))


def build_factory_task_runner(database_path: Path, project_root: Path) -> FactoryTaskRunner:
    """Build the Factory task runner with infrastructure adapters injected."""

    llm_provider = build_llm_provider()
    return FactoryTaskRunner(
        task_repository=build_sql_task_repository(database_path),
        execution_provider=PrefectExecutionProvider(llm_provider=llm_provider),
        prompt_compiler=build_default_task_prompt_compiler(project_root=project_root),
    )
