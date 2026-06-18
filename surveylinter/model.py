"""Core data model for survey-linter.

Everything downstream (rules, scales, importers, report, score) speaks in terms
of these small dataclasses. Stdlib only — no third-party dependencies, ever.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

# Severity levels — kept as short strings so they round-trip cleanly to JSON.
HIGH, MED, LOW = "high", "med", "low"
SEV_EMOJI = {HIGH: "🔴", MED: "🟠", LOW: "🟡"}
SEV_RANK = {HIGH: 3, MED: 2, LOW: 1}
SEV_PENALTY = {HIGH: 12, MED: 6, LOW: 2}  # points subtracted from a 100 baseline


@dataclass
class Finding:
    """One problem found in one item (or in the instrument as a whole)."""
    severity: str          # HIGH | MED | LOW
    code: str              # stable machine id, e.g. "double_barreled"
    name: str              # short human label
    message: str           # why it biases data + how to fix, naming exact wording
    target: str = "question"   # question | scale | structure
    fix: Optional[str] = None  # deterministic rewrite suggestion, if any

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Question:
    """A single survey item plus any response options/scale attached to it."""
    n: int
    text: str
    options: List[str] = field(default_factory=list)  # response anchors / choices
    rows: List[str] = field(default_factory=list)      # matrix sub-statements
    section: Optional[str] = None
    qtype: Optional[str] = None   # single | multi | matrix | scale | rating | open | yesno
    findings: List[Finding] = field(default_factory=list)
    raw: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n": self.n,
            "text": self.text,
            "options": self.options,
            "rows": self.rows,
            "section": self.section,
            "qtype": self.qtype,
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass
class Score:
    """A transparent, deterministic quality score — no black box."""
    value: int                      # 0..100 (higher = cleaner)
    grade: str                      # A..F
    verdict: str                    # ship-ready | minor fixes | needs work
    counts: Dict[str, int]          # {"high": n, "med": n, "low": n}
    questions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Report:
    questions: List[Question]
    structure: List[Finding]
    score: Score
    lang: str = "en"

    def all_findings(self) -> List[Finding]:
        out: List[Finding] = []
        for q in self.questions:
            out.extend(q.findings)
        out.extend(self.structure)
        return out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lang": self.lang,
            "score": self.score.to_dict(),
            "questions": [q.to_dict() for q in self.questions],
            "structure": [f.to_dict() for f in self.structure],
        }
