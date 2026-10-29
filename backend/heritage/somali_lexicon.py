"""Somali-only vocabulary hints for private, local transcription.

This lexicon is a recognition aid, not a dictionary authority. It never rewrites
the transcript and never translates or publishes heritage content.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

LEXICON_PATH = Path(__file__).with_name("somali_lexicon.json")
_WORD_RE = re.compile(r"[^\W_]+(?:[-'][^\W_]+)*", re.UNICODE)


@lru_cache(maxsize=1)
def load_lexicon() -> tuple[dict[str, Any], ...]:
    """Load the bundled lexicon without network access."""
    with LEXICON_PATH.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if payload.get("language") != "so" or not isinstance(payload.get("entries"), list):
        raise ValueError("Le lexique doit contenir uniquement des entrées somalies")
    entries = []
    for item in payload["entries"]:
        word = item.get("word")
        if not isinstance(word, str) or not word.strip():
            continue
        variants = item.get("variants", [])
        if not isinstance(variants, list):
            variants = []
        entries.append({
            "word": word.strip(),
            "variants": tuple(v.strip() for v in variants if isinstance(v, str) and v.strip()),
            "category": str(item.get("category", "general")),
        })
    return tuple(entries)


def vocabulary_prompt(*, max_chars: int = 700) -> str:
    """Build a compact Somali-only prompt for Whisper's initial_prompt."""
    words: list[str] = []
    for entry in load_lexicon():
        words.append(entry["word"])
        words.extend(entry["variants"])
    prompt = ", ".join(dict.fromkeys(words))
    return prompt[:max(0, max_chars)]


def detect_somali_terms(transcript: str) -> list[str]:
    """Return lexicon words/variants found in text, without modifying that text."""
    if not transcript or not transcript.strip():
        return []
    tokens = [token.casefold() for token in _WORD_RE.findall(transcript)]
    token_set = set(tokens)
    found: list[str] = []
    for entry in load_lexicon():
        candidates = (entry["word"], *entry["variants"])
        if any(candidate.casefold() in token_set for candidate in candidates):
            found.append(entry["word"])
    return found


def enrich_result(result: dict[str, Any]) -> dict[str, Any]:
    """Add Somali-only lexical metadata; preserve transcript bytes and meaning."""
    result["mots_somali"] = detect_somali_terms(str(result.get("texte", "")))
    result["lexique_somali_version"] = 1
    return result
