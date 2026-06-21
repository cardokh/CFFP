"""Factory task seed file repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .task_seed_models import FactoryTaskSeed


class JsonFactoryTaskSeedRepository:
    """Loads Factory task seed data from JSON."""

    def load_seeds(self, seed_path: Path) -> tuple[FactoryTaskSeed, ...]:
        """Load seed task definitions from a JSON file."""

        raw_data = self._read_json(seed_path)
        return tuple(self._map_seed(raw_seed) for raw_seed in raw_data.get("tasks", []))

    @staticmethod
    def _map_seed(raw_seed: dict[str, Any]) -> FactoryTaskSeed:
        return FactoryTaskSeed(
            task_id=str(raw_seed["task_id"]),
            name=str(raw_seed["name"]),
            description=str(raw_seed.get("description", "")),
            task_definition_path=str(raw_seed["task_definition_path"]),
            priority=int(raw_seed.get("priority", 100)),
            payload=json.dumps(raw_seed.get("payload", {})),
        )

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)
