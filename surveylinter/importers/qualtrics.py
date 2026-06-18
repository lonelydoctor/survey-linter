"""Parse a Qualtrics QSF export (JSON). Piped text like ${q://...} is kept so the
piped-text rule can flag it."""
from __future__ import annotations

import re
from typing import List

from ..model import Question

_TAG = re.compile(r"<[^>]+>")


def _strip_html(s: str) -> str:
    return _TAG.sub("", s or "").replace("&nbsp;", " ").strip()


def _sort_key(k: str):
    return (0, int(k)) if str(k).isdigit() else (1, str(k))


def _displays(d) -> List[str]:
    if not isinstance(d, dict):
        return []
    return [_strip_html(v.get("Display", "")) for _, v in sorted(d.items(), key=lambda kv: _sort_key(kv[0]))
            if isinstance(v, dict) and v.get("Display")]


def parse(data) -> List[Question]:
    out: List[Question] = []
    n = 0
    for el in data.get("SurveyElements", []) or []:
        if el.get("Element") != "SQ":
            continue
        try:
            p = el.get("Payload", {}) or {}
            text = _strip_html(p.get("QuestionText", ""))
            if not text:
                continue
            qtype_raw = p.get("QuestionType")
            choices = p.get("Choices", {}) or {}
            answers = p.get("Answers", {}) or {}
            opts: List[str] = []
            rows: List[str] = []
            qtype = None
            if qtype_raw == "Matrix":
                rows, opts, qtype = _displays(choices), _displays(answers), "matrix"
            elif qtype_raw == "MC":
                opts = _displays(choices)
                qtype = "multi" if p.get("Selector") in ("MAVR", "MAHR", "MACOL") else "single"
            elif qtype_raw == "TE":
                qtype = "open"
            elif qtype_raw == "Slider":
                qtype = "scale"
            else:
                opts = _displays(choices)
            n += 1
            out.append(Question(n=n, text=text, options=opts, rows=rows, qtype=qtype))
        except (AttributeError, TypeError):
            continue
    return out
