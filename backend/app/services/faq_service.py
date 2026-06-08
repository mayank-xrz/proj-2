"""FAQ resolution service — matches caller questions against the business knowledge base."""

import re
from difflib import SequenceMatcher

from app.config import load_business_config


def resolve_faq(question: str) -> dict | None:
    """Find the best matching FAQ answer for a caller's question.

    Uses a simple similarity ratio; returns None if no match exceeds the
    confidence threshold. Replace with a vector-search / LLM approach for
    production deployments with large knowledge bases.
    """
    config = load_business_config()
    faqs: list[dict] = config.get("faqs", [])
    if not faqs:
        return None

    question_normalized = _normalize(question)
    best_score = 0.0
    best_faq = None

    for faq in faqs:
        faq_q_normalized = _normalize(faq["question"])
        score = SequenceMatcher(None, question_normalized, faq_q_normalized).ratio()
        # Also check for keyword overlap to boost exact-word matches
        score = max(score, _keyword_overlap(question_normalized, faq_q_normalized))
        if score > best_score:
            best_score = score
            best_faq = faq

    if best_score < 0.35:  # Threshold: below this we can't confidently answer
        return None

    return {
        "question": best_faq["question"],
        "answer": best_faq["answer"],
        "confidence": round(best_score, 3),
    }


def get_all_faqs() -> list[dict]:
    """Return the full FAQ list from the business config."""
    config = load_business_config()
    return config.get("faqs", [])


def _normalize(text: str) -> str:
    """Lowercase and strip punctuation for comparison."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def _keyword_overlap(a: str, b: str) -> float:
    """Score based on fraction of words from `a` found in `b`."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a:
        return 0.0
    # Remove common stop-words
    stop = {"do", "you", "i", "the", "a", "an", "is", "are", "what", "how", "can", "my", "me"}
    words_a -= stop
    words_b -= stop
    if not words_a:
        return 0.0
    return len(words_a & words_b) / len(words_a)
