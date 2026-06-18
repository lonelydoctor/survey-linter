"""Linting pipeline: run rules over questions, apply config, score, return Report."""
from __future__ import annotations

from typing import List, Optional

from .model import Report, Question, Finding
from .lexicons import get_lexicon, detect_language
from . import rules as _rules
from . import scales as _scales
from . import structure as _structure
from . import score as _score


def _apply_config(findings: List[Finding], config) -> List[Finding]:
    if not config:
        return findings
    out: List[Finding] = []
    for f in findings:
        if f.code in config.disabled:
            continue
        if f.code in config.severity:
            f.severity = config.severity[f.code]
        out.append(f)
    return out


def lint_questions(questions: List[Question], lang: str = "auto", config=None) -> Report:
    if lang in (None, "", "auto"):
        lang = detect_language(" ".join(q.text for q in questions))
    if config and getattr(config, "language", None):
        lang = config.language
    lex = get_lexicon(lang)

    for q in questions:
        if config and config.is_ignored(q.text):
            q.findings = []
            continue
        fs: List[Finding] = []
        for rule in _rules.QUESTION_RULES:
            fs.extend(rule(q, lex))
        for row in (q.rows or []):
            sub = Question(n=q.n, text=row)
            for rule in _rules.QUESTION_RULES:
                for f in rule(sub, lex):
                    f.message = f"[{row[:24]}…] " + f.message
                    fs.append(f)
        if q.options:
            for rule in _scales.SCALE_RULES:
                fs.extend(rule(q, lex))
        q.findings = _apply_config(fs, config)

    structure = _apply_config(_structure.run(questions, lex), config)
    sc = _score.compute(questions, structure)
    return Report(questions=questions, structure=structure, score=sc, lang=lang)
