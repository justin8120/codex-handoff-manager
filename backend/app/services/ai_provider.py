import os
from dataclasses import dataclass
from typing import Literal


ProviderName = Literal["openai", "gemini", "mock"]

ROMANIZED_MEAL_NAMES = {
    "chicken steak and egg noodles": "\u96de\u6392\u86cb\u9eb5",
    "steak and egg noodles": "\u725b\u6392\u86cb\u9eb5",
    "chicken steak with noodles": "\u96de\u6392\u9eb5",
    "steak with noodles": "\u725b\u6392\u9eb5",
    "steak and eggs": "\u725b\u6392\u86cb",
    "chicken steak": "\u96de\u6392",
    "chicken noodles": "\u96de\u8089\u9eb5",
    "steak": "\u725b\u6392",
    "eggs": "\u96de\u86cb",
    "noodles": "\u9eb5\u98df",
    "shrimp fried rice": "\u8766\u4ec1\u7092\u98ef",
    "katsudon": "\u8c6c\u6392\u4e3c",
    "oyakodon": "\u89aa\u5b50\u4e3c",
    "butadon": "\u8c5a\u4e3c",
    "gyudon": "\u725b\u4e3c",
    "tendon": "\u5929\u4e3c",
    "curry rice": "\u5496\u54e9\u98ef",
    "fried rice": "\u7092\u98ef",
}

MEAL_NAME_ALIASES = {
    "\u8c5a\u4e95": "\u8c5a\u4e3c",
    "\u8c6c\u8089\u4e3c": "\u8c5a\u4e3c",
    "\u8c5a\u8089\u4e3c": "\u8c5a\u4e3c",
}

USER_FACING_TERMS = {
    "steak": "\u725b\u6392",
    "beef": "\u725b\u8089",
    "noodles": "\u9eb5\u689d",
    "greens": "\u9752\u83dc",
    "soup": "\u9ad8\u6e6f",
    "broth": "\u9ad8\u6e6f",
    "pork slices": "\u8c6c\u8089\u7247",
    "chicken chunks": "\u96de\u8089\u584a",
    "chicken": "\u96de\u8089",
    "pork": "\u8c6c\u8089",
    "egg": "\u86cb",
    "rice": "\u767d\u98ef",
    "nori": "\u6d77\u82d4",
    "japanese": "\u65e5\u5f0f",
    "donburi": "\u4e3c\u98ef",
    "cutlet": "\u8c6c\u6392",
    "breading": "\u9eb5\u8863",
}


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


def web_verify_enabled() -> bool:
    return os.getenv("WEB_VERIFY_ENABLED", "true").lower() == "true"


def web_verify_provider() -> str:
    return os.getenv("WEB_VERIFY_PROVIDER", "gemini_grounding")


def web_verify_max_candidates() -> int:
    return int(os.getenv("WEB_VERIFY_MAX_CANDIDATES", "5"))


def web_verify_min_confidence() -> float:
    return float(os.getenv("WEB_VERIFY_MIN_CONFIDENCE", "0.65"))


def gemini_grounding_model() -> str:
    return os.getenv("GEMINI_GROUNDING_MODEL", "gemini-2.5-flash")


def normalize_meal_name(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return text

    lowered = text.lower()
    if lowered in ROMANIZED_MEAL_NAMES:
        return ROMANIZED_MEAL_NAMES[lowered]
    if text in MEAL_NAME_ALIASES:
        return MEAL_NAME_ALIASES[text]

    normalized = text
    for source, target in MEAL_NAME_ALIASES.items():
        normalized = normalized.replace(source, target)
    for source, target in ROMANIZED_MEAL_NAMES.items():
        normalized = _replace_case_insensitive(normalized, source, target)
    return normalized


def normalize_user_facing_text(value: str) -> str:
    normalized = normalize_meal_name(value)
    for source, target in USER_FACING_TERMS.items():
        normalized = _replace_case_insensitive(normalized, source, target)
    return normalized


def normalize_user_facing_list(values: list[str]) -> list[str]:
    return [normalize_user_facing_text(value) for value in values]


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
    return AiProvider(name="mock", model="system-analysis", api_key=None)


def _replace_case_insensitive(text: str, source: str, target: str) -> str:
    lowered = text.lower()
    index = lowered.find(source)
    while index != -1:
        text = f"{text[:index]}{target}{text[index + len(source):]}"
        lowered = text.lower()
        index = lowered.find(source, index + len(target))
    return text
