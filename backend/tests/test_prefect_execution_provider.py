"""Prefect execution provider tests."""

from __future__ import annotations

from src.core.factory.task_execution_models import FactoryTaskExecutionRequest
from src.infrastructure.ai.mock.mock_llm_provider import MockLlmProvider
from src.infrastructure.orchestration.prefect.prefect_execution_provider import (
    PrefectExecutionProvider,
)


def test_prefect_execution_provider_returns_successful_result() -> None:
    result = PrefectExecutionProvider(llm_provider=MockLlmProvider()).execute(
        FactoryTaskExecutionRequest(
            task_id="factory.prefect-smoke",
            name="Prefect Smoke Task",
            task_definition_path="tasks/prefect-smoke.json",
            priority=10,
            payload={"scope": "test"},
            prompt="Generate a smoke-test artifact.",
            system_instruction="Use concise output.",
        )
    )

    assert result.task_id == "factory.prefect-smoke"
    assert result.success is True
    assert result.message.startswith("Factory task executed by Prefect provider;")
    assert result.artifact_text is not None
