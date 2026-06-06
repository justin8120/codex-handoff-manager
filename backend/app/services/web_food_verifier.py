import json
import os
from typing import Any

from app.services.ai_provider import (
    gemini_grounding_model,
    normalize_meal_name,
    normalize_user_facing_text,
    web_verify_enabled,
    web_verify_max_candidates,
    web_verify_min_confidence,
    web_verify_provider,
)


BUTADON = "\u8c5a\u4e3c"
PORK_DONBURI = "\u8c6c\u8089\u4e3c"
OYAKODON = "\u89aa\u5b50\u4e3c"
KATSUDON = "\u8c6c\u6392\u4e3c"
JAPANESE_DONBURI = "\u65e5\u5f0f\u4e3c\u98ef"
PORK_SLICES = "\u8c6c\u8089\u7247"
PORK_MEAT = "\u8c5a\u8089"
LARGE_MEAT_SLICES = "\u5927\u7247\u8089\u7247"
CHICKEN_MEAT = "\u96de\u8089"
CHICKEN_BLOCKS = "\u96de\u8089\u584a"
FRIED_PORK_CUTLET = "\u70b8\u8c6c\u6392"
BREADING = "\u9eb5\u8863"
EGG = "\u86cb"
RICE = "\u98ef"
NORI = "\u6d77\u82d4"
BUTADON_REASON = (
    "\u6b64\u9910\u9ede\u8207\u89aa\u5b50\u4e3c\u5916\u89c0\u76f8\u4f3c\uff0c"
    "\u56e0\u53ef\u898b\u8089\u7247\u8f03\u63a5\u8fd1\u8c6c\u8089\uff0c"
    "\u7cfb\u7d71\u5224\u65b7\u70ba\u8c5a\u4e3c"
)
OYAKODON_REJECT_REASON = (
    "\u5716\u7247\u672a\u660e\u78ba\u986f\u793a\u96de\u8089\u584a\uff0c"
    "\u4e14\u8089\u7247\u5916\u89c0\u8f03\u50cf\u8c6c\u8089"
)


def verify_food_candidates(candidates: list[dict[str, Any]], visual_description: str) -> dict[str, Any]:
    local_result = rerank_food_candidates(candidates, visual_description)
    if not web_verify_enabled() or web_verify_provider() != "gemini_grounding":
        return local_result

    try:
        grounded_result = _try_gemini_grounding(candidates, visual_description)
    except Exception as error:
        print(f"Web verification failed: {error}")
        return local_result

    if not grounded_result:
        return local_result
    if float(grounded_result.get("confidence") or 0) < web_verify_min_confidence():
        return local_result
    return _merge_verification(local_result, grounded_result)


def rerank_food_candidates(candidates: list[dict[str, Any]], visual_description: str) -> dict[str, Any]:
    limited = candidates[: max(web_verify_max_candidates(), 1)]
    evidence_text = _combined_evidence(limited, visual_description)
    has_pork = _has_any(evidence_text, [PORK_SLICES, PORK_MEAT, LARGE_MEAT_SLICES, "pork slices", "butadon"])
    has_chicken = _has_any(evidence_text, [CHICKEN_MEAT, CHICKEN_BLOCKS, "chicken", "oyakodon"])
    has_no_cutlet = _has_any(
        evidence_text,
        [
            "\u6c92\u6709\u70b8\u8c6c\u6392",
            "\u672a\u898b\u70b8\u8c6c\u6392",
            "\u770b\u4e0d\u5230\u70b8\u8c6c\u6392",
            "\u6c92\u6709\u9eb5\u8863",
            "\u672a\u898b\u9eb5\u8863",
            "no visible fried pork cutlet",
            "no fried pork cutlet",
            "no visible cutlet",
            "no breading",
        ],
    )
    has_cutlet = (
        _has_any(evidence_text, [FRIED_PORK_CUTLET, BREADING, "\u8c6c\u6392", "cutlet", "katsu", "breading"])
        and not has_no_cutlet
    )
    has_only_egg_rice = _has_any(evidence_text, [EGG, "egg"]) and _has_any(evidence_text, [RICE, "rice"]) and not has_chicken

    scored: list[dict[str, Any]] = []
    for candidate in limited:
        item = dict(candidate)
        name = normalize_meal_name(str(item.get("name") or ""))
        item["name"] = name
        score = max(0.0, min(float(item.get("confidence") or 0.45), 1.0))
        candidate_text = f"{name} {_combined_evidence([item], '')}".lower()

        if _is_butadon_name(name) and has_pork:
            score += 0.18
        if _is_oyakodon_name(name) and has_chicken:
            score += 0.14
        if _is_oyakodon_name(name) and has_only_egg_rice:
            score -= 0.1
        if _is_oyakodon_name(name) and not has_chicken:
            score = min(score, 0.75)
        if _is_butadon_name(name) and _has_any(candidate_text, [PORK_SLICES, PORK_MEAT, "pork"]):
            score += 0.08
        if _is_katsudon_name(name) and has_cutlet:
            score += 0.12
        if _is_katsudon_name(name) and not has_cutlet:
            score -= 0.22

        item["rerankScore"] = max(0.0, min(score, 1.0))
        scored.append(item)

    if not scored:
        return _default_verification(visual_description)

    scored.sort(key=lambda item: float(item.get("rerankScore") or 0), reverse=True)
    winner = scored[0]
    runner_up = scored[1] if len(scored) > 1 else None
    winner_name = normalize_meal_name(str(winner.get("name") or BUTADON))
    gap = float(winner.get("rerankScore") or 0) - float((runner_up or {}).get("rerankScore") or 0)

    if has_pork and not has_chicken and _has_any(evidence_text, [LARGE_MEAT_SLICES, PORK_SLICES, "pork slices"]):
        winner_name = BUTADON if BUTADON in _names(scored) else PORK_DONBURI
        winner["rerankScore"] = max(float(winner.get("rerankScore") or 0), web_verify_min_confidence())

    matched_evidence = _string_list(winner.get("evidence"))
    if has_pork:
        matched_evidence = _add_unique(matched_evidence, "\u7167\u7247\u4e2d\u4e3b\u8981\u662f\u8089\u7247\u8986\u84cb\u767d\u98ef")
    if _is_butadon_name(winner_name):
        matched_evidence = _add_unique(matched_evidence, "\u89aa\u5b50\u4e3c\u901a\u5e38\u4ee5\u96de\u8089\u8207\u86cb\u70ba\u4e3b\u8981\u7279\u5fb5")

    confidence = max(float(winner.get("rerankScore") or 0.65), web_verify_min_confidence())
    if _is_oyakodon_name(winner_name) and not has_chicken:
        confidence = min(confidence, 0.75)

    reason = _verification_reason(winner_name, gap, has_pork, has_chicken)
    return {
        "verifiedName": winner_name,
        "verifiedType": JAPANESE_DONBURI if _is_donburi_name(winner_name) else str(winner.get("mealType") or ""),
        "confidence": max(0.0, min(confidence, 1.0)),
        "matchedEvidence": matched_evidence,
        "rejectedCandidates": _rejected_candidates(scored, winner_name, has_pork, has_chicken),
        "sources": [],
        "reason": normalize_user_facing_text(reason),
    }


def _try_gemini_grounding(candidates: list[dict[str, Any]], visual_description: str) -> dict[str, Any] | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    from google import genai  # type: ignore[import-not-found]
    from google.genai import types  # type: ignore[import-not-found]

    client = genai.Client(api_key=api_key)
    prompt = (
        "Use Google Search grounding to compare these food candidates against the visual evidence. "
        "Focus on distinguishing butadon pork rice bowl from oyakodon chicken egg rice bowl. "
        "Return only JSON with keys: verifiedName, verifiedType, confidence, matchedEvidence, "
        "rejectedCandidates, sources. No markdown.\n"
        f"Visual description: {visual_description}\n"
        f"Candidates: {json.dumps(candidates, ensure_ascii=False)}\n"
        "Useful search queries include: "
        "\u8c5a\u4e3c \u8c6c\u8089\u7247 \u86cb \u767d\u98ef \u6d77\u82d4 \u5716\u7247; "
        "\u89aa\u5b50\u4e3c \u96de\u8089 \u86cb \u767d\u98ef \u6d77\u82d4 \u5716\u7247; "
        "\u8c5a\u4e3c vs \u89aa\u5b50\u4e3c \u5dee\u7570; "
        "butadon pork rice bowl egg nori; oyakodon chicken egg rice bowl."
    )
    response = client.models.generate_content(
        model=gemini_grounding_model(),
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            response_mime_type="application/json",
        ),
    )
    text = getattr(response, "text", "") or ""
    if not text:
        return None
    payload = json.loads(text)
    sources = _extract_sources(response)
    if sources and not payload.get("sources"):
        payload["sources"] = sources
    return payload


def _extract_sources(response: Any) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        metadata = getattr(candidate, "grounding_metadata", None) or getattr(candidate, "groundingMetadata", None)
        chunks = getattr(metadata, "grounding_chunks", None) or getattr(metadata, "groundingChunks", None) or []
        for chunk in chunks:
            web = getattr(chunk, "web", None)
            title = getattr(web, "title", "") if web else ""
            uri = getattr(web, "uri", "") if web else ""
            if uri:
                sources.append({"title": title or uri, "url": uri})
    return sources


def _merge_verification(local_result: dict[str, Any], grounded_result: dict[str, Any]) -> dict[str, Any]:
    merged = dict(local_result)
    for key in ["verifiedName", "verifiedType", "confidence", "matchedEvidence", "rejectedCandidates", "sources"]:
        if grounded_result.get(key):
            merged[key] = grounded_result[key]
    if merged.get("verifiedName"):
        merged["verifiedName"] = normalize_meal_name(str(merged["verifiedName"]))
    if merged.get("verifiedType"):
        merged["verifiedType"] = normalize_user_facing_text(str(merged["verifiedType"]))
    if merged.get("matchedEvidence"):
        merged["matchedEvidence"] = [normalize_user_facing_text(str(item)) for item in merged["matchedEvidence"]]
    if not merged.get("reason"):
        merged["reason"] = local_result.get("reason", "")
    merged["reason"] = normalize_user_facing_text(str(merged.get("reason") or ""))
    return merged


def _default_verification(visual_description: str) -> dict[str, Any]:
    name = BUTADON if _has_any(visual_description, [PORK_SLICES, PORK_MEAT, "pork"]) else "\u7591\u4f3c\u8c5a\u4e3c"
    return {
        "verifiedName": name,
        "verifiedType": JAPANESE_DONBURI,
        "confidence": web_verify_min_confidence(),
        "matchedEvidence": [visual_description] if visual_description else [],
        "rejectedCandidates": [],
        "sources": [],
        "reason": BUTADON_REASON,
    }


def _verification_reason(winner_name: str, gap: float, has_pork: bool, has_chicken: bool) -> str:
    if _is_butadon_name(winner_name) and (gap < 0.15 or (has_pork and not has_chicken)):
        return BUTADON_REASON
    if _is_butadon_name(winner_name):
        return (
            "\u7167\u7247\u4e2d\u8089\u7247\u8207\u767d\u98ef\u7684\u7d44\u5408"
            "\u66f4\u63a5\u8fd1\u8c5a\u4e3c\u7279\u5fb5\u3002"
        )
    return (
        "\u7cfb\u7d71\u5df2\u6839\u64da\u5019\u9078\u9910\u9ede\u8207"
        "\u53ef\u898b\u98df\u6750\u7279\u5fb5\u91cd\u65b0\u6821\u6b63\u8fa8\u8b58\u7d50\u679c\u3002"
    )


def _rejected_candidates(
    scored: list[dict[str, Any]],
    winner_name: str,
    has_pork: bool,
    has_chicken: bool,
) -> list[dict[str, str]]:
    rejected: list[dict[str, str]] = []
    for item in scored:
        name = normalize_meal_name(str(item.get("name") or ""))
        if name == winner_name:
            continue
        reason = "\u8207\u6700\u7d42\u8fa8\u8b58\u7684\u98df\u6750\u7279\u5fb5\u4e0d\u5982\u4e3b\u5019\u9078\u7b26\u5408"
        if _is_oyakodon_name(name) and has_pork and not has_chicken:
            reason = OYAKODON_REJECT_REASON
        rejected.append({"name": name, "reason": reason})
    return rejected


def _combined_evidence(candidates: list[dict[str, Any]], visual_description: str) -> str:
    chunks = [visual_description]
    for candidate in candidates:
        chunks.append(str(candidate.get("name") or ""))
        chunks.extend(_string_list(candidate.get("evidence")))
    return " ".join(chunks).lower()


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value:
        return [value]
    return []


def _names(candidates: list[dict[str, Any]]) -> list[str]:
    return [normalize_meal_name(str(candidate.get("name") or "")) for candidate in candidates]


def _is_butadon_name(name: str) -> bool:
    normalized = normalize_meal_name(name)
    return BUTADON in normalized or PORK_DONBURI in normalized


def _is_oyakodon_name(name: str) -> bool:
    return OYAKODON in normalize_meal_name(name)


def _is_katsudon_name(name: str) -> bool:
    return KATSUDON in normalize_meal_name(name)


def _is_donburi_name(name: str) -> bool:
    normalized = normalize_meal_name(name)
    return _is_butadon_name(normalized) or _is_oyakodon_name(normalized) or _is_katsudon_name(normalized) or "\u4e3c" in normalized


def _has_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _add_unique(values: list[str], value: str) -> list[str]:
    return values if value in values else [*values, value]
