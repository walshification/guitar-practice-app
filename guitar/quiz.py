"""Shared utilities for interactive quiz commands."""

from dataclasses import dataclass, field


@dataclass
class Question:
    correct: str
    options: list[str] = field(default_factory=list)


def resolve_answer(raw: str, options: list[str]) -> str:
    """Accept a 1-based number or literal option text."""
    raw = raw.strip()
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            return options[idx]
    return raw


def score_summary(score: int, total: int) -> str:
    pct = int(score / total * 100) if total else 0
    return f"{score}/{total} ({pct}%)"
