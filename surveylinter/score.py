"""Transparent, deterministic quality score.

No machine-learning black box: start at 100 and subtract a fixed penalty per
finding by severity. The exact arithmetic is shown in the report so the user can
reproduce it by hand.
"""
from __future__ import annotations

from typing import List

from .model import Score, Finding, Question, HIGH, MED, LOW, SEV_PENALTY


def compute(questions: List[Question], structure: List[Finding]) -> Score:
    findings: List[Finding] = [f for q in questions for f in q.findings] + list(structure)
    counts = {HIGH: 0, MED: 0, LOW: 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    penalty = sum(SEV_PENALTY[s] * n for s, n in counts.items())
    value = max(0, 100 - penalty)
    grade = ("A" if value >= 90 else "B" if value >= 80 else
             "C" if value >= 70 else "D" if value >= 60 else "F")
    if not findings:
        verdict = "ship-ready"
    elif counts[HIGH]:
        verdict = "needs work"
    else:
        verdict = "minor fixes"
    return Score(value=value, grade=grade, verdict=verdict, counts=counts, questions=len(questions))
