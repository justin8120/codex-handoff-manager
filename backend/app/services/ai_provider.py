import os
from dataclasses import dataclass
from typing import Literal


ProviderName = Literal["openai", "gemini", "mock"]


@dataclass(frozen=True)
class AiProvider:
    name: ProviderName
    model: str
    api_key: str | None
    base_url: str | None = None

    @property
    def configured(self) -> bool:
        return self.name == "mock" or bool(self.api_key)


def fallback_enabled() -> bool:
    return os.getenv("AI_FALLBACK_ENABLED", "true").lower() == "true"


def get_ai_provider() -> AiProvider:
    requested = os.getenv("AI_PROVIDER", "auto").lower()
    if requested == "openai":
        return _openai_provider()
    if requested == "gemini":
        return _gemini_provider()
    if requested == "mock":
        return _mock_provider()
    return _auto_provider()


def _auto_provider() -> AiProvider:
    if os.getenv("GEMINI_API_KEY"):
        return _gemini_provider()
    if os.getenv("OPENAI_API_KEY"):
        return _openai_provider()
    return _mock_provider()


def _openai_provider() -> AiProvider:
    return AiProvider(
        name="openai",
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def _gemini_provider() -> AiProvider:
    return AiProvider(
        name="gemini",
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
    )


def _mock_provider() -> AiProvider:
    return AiProvider(name="mock", model="rule-based-fallback", api_key=None)
