"""Tiny shared helpers."""
from __future__ import annotations


def L(lex, en: str, zh: str) -> str:
    """Pick a message in the lexicon's language."""
    return zh if getattr(lex, "cjk", False) else en
