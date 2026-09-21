"""Deterministic local response adapter used by the compatibility interface."""

from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Cardiorenal Syndrome Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} deterministic local mock] "
            "No external model was called. "
            f"Query received: {prompt[:120]}"
        )


class LLMFactory:
    @staticmethod
    def create(provider: str = "mock", system_name: str = "Cardiorenal Syndrome Agent"):
        normalized = str(provider).strip().lower()
        if normalized in {"mock", "deterministic", "test"}:
            return MockLLM(system_name)
        raise ValueError(
            f"Unsupported model provider {provider!r}. "
            "This repository currently implements only the deterministic local mock."
        )
