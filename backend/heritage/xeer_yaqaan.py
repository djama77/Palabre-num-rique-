"""Local, source-grounded retrieval for the Xeer-Ciise reference.

This module retrieves evidence from OCR text; it does not invent answers and
does not call an external AI service. Text files must contain page markers:
[[PAGE 1]], [[PAGE 2]], etc. Human review of OCR is required.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

PAGE_MARKER = re.compile(r"\[\[PAGE\s+(\d+)\]\]", re.IGNORECASE)


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()


def load_passages(path: str | Path) -> list[dict]:
    """Load OCR text and return page-level passages with original page numbers."""
    source = Path(path)
    text = source.read_text(encoding="utf-8-sig")
    matches = list(PAGE_MARKER.finditer(text))
    if not matches:
        raise ValueError(
            "Marqueurs de pages absents. Le texte doit contenir [[PAGE 1]], "
            "[[PAGE 2]], etc. Utilisez prepare_xeer_pdf.py."
        )
    passages = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if body:
            passages.append({
                "page": int(match.group(1)),
                "text": body,
                "normalized": _normalize(body),
            })
    return passages


def search_evidence(question: str, source_path: str | Path, *, limit: int = 5) -> dict:
    """Return relevant page passages; never claim a final answer without evidence."""
    if not question or not question.strip():
        raise ValueError("Veuillez saisir une question.")
    if limit < 1 or limit > 10:
        raise ValueError("La limite doit être comprise entre 1 et 10.")
    passages = load_passages(source_path)
    terms = set(_normalize(question).split())
    terms = {term for term in terms if len(term) > 1}
    if not terms:
        return {"question": question, "found": False, "message": "Question trop courte.", "sources": []}

    scored = []
    for passage in passages:
        words = set(passage["normalized"].split())
        overlap = terms & words
        if overlap:
            score = len(overlap) / max(1, len(terms))
            scored.append((score, len(overlap), passage))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    sources = [
        {"page": passage["page"], "score": round(score, 3), "text": passage["text"]}
        for score, _, passage in scored[:limit]
    ]
    return {
        "question": question,
        "found": bool(sources),
        "message": (
            "Extraits trouvés dans le document OCR. Vérifiez le texte avec le PDF original avant de citer."
            if sources else
            "Aucun passage pertinent trouvé dans l'index disponible. Ne pas inventer de réponse ; vérifier le PDF et son OCR."
        ),
        "sources": sources,
    }
