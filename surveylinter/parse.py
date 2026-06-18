"""Parse plain text / markdown / CSV into Question objects.

Handles numbered or bulleted items, sections (markdown headings), inline scales
("Rate our service: 0-5, 5-10") and standalone option lines that attach to the
question above them. Works for both space-delimited and CJK text.
"""
from __future__ import annotations

import csv
import io
import re
from typing import List, Optional

from .model import Question

_BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)]|Q\d+[.)：:]?|第?\s*\d+\s*[、.)])\s*", re.I)
_SPLIT = re.compile(r"[,，、/|]|\s-\s| \| ")


def clean(line: str) -> str:
    return _BULLET.sub("", line.strip()).strip()


def split_options(s: str) -> List[str]:
    return [p.strip() for p in _SPLIT.split(s) if p.strip()]


def _looks_like_options(s: str) -> bool:
    """True if the whole line is a bare list of anchors (no question stem)."""
    if ":" in s or "：" in s:
        return False
    if re.fullmatch(r"\s*\d+\s*[-–—]\s*\d+\s*", s):
        return True
    if s.rstrip().endswith(("?", "？")):
        return False
    parts = split_options(s)
    return len(parts) >= 3 and len(s) < 160


def _inline_options(text: str) -> Optional[List[str]]:
    """Extract a scale embedded after a stem, e.g. 'Rate service: 0-5, 5-10'."""
    m = re.search(r"[:：]\s*(.+)$", text)
    if not m:
        return None
    tail = m.group(1)
    parts = split_options(tail)
    if re.search(r"\d+\s*[-–—]\s*\d+", tail) or len(parts) >= 3:
        return parts or None
    return None


def parse_plaintext(text: str) -> List[Question]:
    questions: List[Question] = []
    qn = 0
    for raw in text.splitlines():
        s = clean(raw)
        if not s:
            continue
        if _looks_like_options(s) and questions:
            questions[-1].options.extend(split_options(s))
            continue
        qn += 1
        q = Question(n=qn, text=s, raw=raw)
        inline = _inline_options(s)
        if inline:
            q.options = inline
        questions.append(q)
    return questions


def parse_markdown(text: str) -> List[Question]:
    questions: List[Question] = []
    qn = 0
    section: Optional[str] = None
    in_fence = False
    for raw in text.splitlines():
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        h = re.match(r"^\s{0,3}#{1,6}\s+(.*)$", raw)
        if h:
            section = h.group(1).strip()
            continue
        s = clean(raw)
        if not s:
            continue
        if _looks_like_options(s) and questions:
            questions[-1].options.extend(split_options(s))
            continue
        qn += 1
        q = Question(n=qn, text=s, section=section, raw=raw)
        inline = _inline_options(s)
        if inline:
            q.options = inline
        questions.append(q)
    return questions


def parse_csv(text: str) -> List[Question]:
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return []
    header = [h.strip().lower() for h in rows[0]]
    q_names = {"question", "item", "text", "prompt", "题目", "问题"}
    o_names = {"options", "scale", "choices", "answers", "选项", "量表"}
    s_names = {"section", "block", "分区", "模块"}
    t_names = {"type", "qtype", "类型"}
    qcol = ocol = scol = tcol = None
    if any(h in q_names for h in header):
        for i, h in enumerate(header):
            if h in q_names and qcol is None:
                qcol = i
            elif h in o_names and ocol is None:
                ocol = i
            elif h in s_names and scol is None:
                scol = i
            elif h in t_names and tcol is None:
                tcol = i
        data = rows[1:]
    else:
        qcol = 0
        ocol = 1 if len(header) > 1 else None
        data = rows
    out: List[Question] = []
    qn = 0
    for r in data:
        if not r or qcol >= len(r) or not r[qcol].strip():
            continue
        qn += 1
        opts: List[str] = []
        if ocol is not None and ocol < len(r) and r[ocol].strip():
            opts = [p.strip() for p in re.split(r"[;,，、|/]", r[ocol]) if p.strip()]
        out.append(Question(
            n=qn, text=clean(r[qcol]), options=opts,
            section=(r[scol].strip() if scol is not None and scol < len(r) and r[scol].strip() else None),
            qtype=(r[tcol].strip() if tcol is not None and tcol < len(r) and r[tcol].strip() else None),
        ))
    return out
