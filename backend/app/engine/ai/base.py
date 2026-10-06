"""Base interfaces and constants for Phase 7 AI Analyst subsystem."""

import abc
from typing import Dict, Any, Optional

AI_METHODOLOGY_VERSION = "v1.0.0-phase7"


class BaseLLMProvider(abc.ABC):
    """Abstract interface for LLM backends (deterministic local, Gemini, OpenAI)."""

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Name of the provider backend."""
        pass

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """Name of the active model."""
        pass

    @abc.abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> str:
        """Generate conversational analytical text."""
        pass

    @abc.abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        context: Dict[str, Any],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate strictly structured output adhering to schema."""
        pass
