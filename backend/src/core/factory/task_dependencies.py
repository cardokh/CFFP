"""Factory task dependency composition."""

from __future__ import annotations

from pathlib import Path

from backend.src.ccore.infrastructure.database import DatabaseManager

from src.infrastructure.persistence.sqlite.factory.sql_task_repository import (
    SqlTaskRepository,
)
from .interfaces.task_repository import ITaskRepository


def build_sql_task_repository(database_path: Path) -> ITaskRepository:
    """Build the configured SQL task repository implementation."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    return SqlTaskRepository(DatabaseManager(str(database_path)))
