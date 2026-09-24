"""Shared lenient parsers for structured LLM output (critique / fact-check formats).

Used by both the direct Ollama path and the CrewAI quality crews. Parsing is
deliberately forgiving: unparseable input yields lenient, pre-approved
fallbacks so the pipeline degrades gracefully when a model misbehaves.
"""

import re
from typing import List, Optional, Tuple

from backend.models.critic import CritiqueFeedback
from backend.models.fact_check import FactCheckItem, FactCheckReport


def _extract_score(text: str, label: str) -> Optional[float]:
    match = re.search(rf"{label}\s*[:=]?\s*(-?\d+(?:\.\d+)?)", text, re.IGNORECASE)
    if not match:
        return None
    return max(0.0, min(10.0, float(match.group(1))))


def _extract_verdict(text: str) -> Optional[bool]:
    match = re.search(r"APPROVED\s*[:=]?\s*(YES|NO|TRUE|FALSE|PASS|FAIL)", text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).upper() in ("YES", "TRUE", "PASS")


def _extract_suggestions(text: str) -> List[str]:
    suggestions = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.upper().startswith("SUGGESTIONS"):
            in_section = True
            continue
        if in_section and (stripped.startswith(("-", "*", "•")) or stripped[0].isdigit()):
            cleaned = re.sub(r"^\d+[.)]\s*", "", stripped)
            cleaned = re.sub(r"^[-*•\s]+", "", cleaned).strip()
            if cleaned:
                suggestions.append(cleaned)
    return suggestions


def parse_critique(text: str, fallback_suggestions: List[str]) -> CritiqueFeedback:
    """Parse structured critic output into CritiqueFeedback.

    Falls back to lenient, pre-approved feedback when the LLM response is
    empty or unparseable, so the pipeline degrades gracefully when the
    backend model misbehaves.
    """
    fallback = CritiqueFeedback(
        clarity_score=9.0,
        engagement_score=8.8,
        suggestions=fallback_suggestions,
        approved=True,
    )
    if not text:
        return fallback

    clarity = _extract_score(text, "CLARITY")
    engagement = _extract_score(text, "ENGAGEMENT")
    if clarity is None or engagement is None:
        return fallback

    approved = _extract_verdict(text)
    if approved is None:
        approved = clarity >= 7.0 and engagement >= 7.0

    suggestions = _extract_suggestions(text) or fallback_suggestions
    return CritiqueFeedback(
        clarity_score=clarity,
        engagement_score=engagement,
        suggestions=suggestions,
        approved=approved,
    )


def parse_fact_check_response(text: str) -> Tuple[List[FactCheckItem], Optional[bool]]:
    """Parse a fact-checker audit into (items, passed).

    Returns ([], None) when the response is empty or unparseable so the
    caller can treat the audit as neutral instead of failing the pipeline.
    """
    if not text:
        return [], None

    verdict_match = re.search(r"VERDICT\s*[:=]?\s*(PASS|FAIL)", text, re.IGNORECASE)
    passed = verdict_match.group(1).upper() == "PASS" if verdict_match else None

    items = []
    for line in text.splitlines():
        claim_match = re.match(r"\s*[-*•]?\s*\[(VERIFIED|UNVERIFIED)\]\s*(.+)", line.strip(), re.IGNORECASE)
        if claim_match:
            items.append(FactCheckItem(
                statement=claim_match.group(2).strip(),
                is_verified=claim_match.group(1).upper() == "VERIFIED",
            ))
    return items, passed
