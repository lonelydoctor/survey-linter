"""Language rule-packs (lexicons).

A Lexicon is the *only* place language-specific knowledge lives. Adding a new
language = adding one module here; the rule engine is language-agnostic and
simply reads these fields. This is what makes survey-linter multilingual without
forking the logic.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class Lexicon:
    code: str                      # "en", "zh", ...
    name: str
    cjk: bool = False              # True for space-less scripts (substring matching)
    length_unit: str = "word"      # "word" | "char"
    length_max: int = 25

    loaded: List[str] = field(default_factory=list)
    absolutes: List[str] = field(default_factory=list)
    vague: List[str] = field(default_factory=list)
    presupposition: List[str] = field(default_factory=list)
    sensitive: List[str] = field(default_factory=list)
    neutral_tokens: List[str] = field(default_factory=list)
    pos_anchors: List[str] = field(default_factory=list)
    neg_anchors: List[str] = field(default_factory=list)
    conjunctions: List[str] = field(default_factory=list)   # double-barreled cues
    negations: List[str] = field(default_factory=list)       # double-negative cues
    referents: List[str] = field(default_factory=list)       # ambiguous pronouns
    other_tokens: List[str] = field(default_factory=list)    # "Other"/"None of these"
    jargon_ok: Set[str] = field(default_factory=set)
    recall_patterns: List[str] = field(default_factory=list)  # regex strings

    def has(self, text: str, words: List[str]) -> List[str]:
        """Return which of `words` appear in `text` (script-aware matching)."""
        low = text.lower()
        hits: List[str] = []
        if self.cjk:
            for w in words:
                wl = w.lower()
                if re.search(r"[A-Za-z]", w):           # ascii term: word-boundary
                    if re.search(r"(?<![A-Za-z])" + re.escape(wl) + r"(?![A-Za-z])", low):
                        hits.append(w)
                elif wl in low:                          # cjk term: substring
                    hits.append(w)
        else:
            padded = " " + re.sub(r"[^\w\s/']", " ", low) + " "
            for w in words:
                if re.search(r"(?<!\w)" + re.escape(w.lower()) + r"(?!\w)", padded):
                    hits.append(w)
        return hits

    def length(self, text: str) -> int:
        if self.length_unit == "char":
            return len(re.findall(r"[㐀-鿿豈-﫿]", text)) or len(text)
        return len(text.split())


_REGISTRY: Dict[str, Lexicon] = {}


def register(lex: Lexicon) -> None:
    _REGISTRY[lex.code] = lex


def get_lexicon(lang: str = "en") -> Lexicon:
    if lang in (None, "", "auto"):
        lang = "en"
    if lang not in _REGISTRY:
        raise KeyError(f"unknown language '{lang}'. available: {sorted(_REGISTRY)}")
    return _REGISTRY[lang]


def available() -> List[str]:
    return sorted(_REGISTRY)


def detect_language(text: str) -> str:
    """Pick a lexicon from the text. CJK-heavy -> zh, else en. Extensible."""
    cjk = len(re.findall(r"[㐀-鿿豈-﫿]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk and cjk * 3 >= latin:   # CJK is information-dense; weight it
        return "zh"
    return "en"


# Register built-in lexicons on import.
from . import en as _en      # noqa: E402
from . import zh as _zh      # noqa: E402

register(_en.LEXICON)
register(_zh.LEXICON)
