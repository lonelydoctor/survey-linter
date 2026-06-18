"""Parse a Google Forms API JSON export (the Forms `get` response shape)."""
from __future__ import annotations

from typing import List

from ..model import Question

_CHOICE_TYPE = {"RADIO": "single", "CHECKBOX": "multi", "DROP_DOWN": "single"}


def parse(data) -> List[Question]:
    out: List[Question] = []
    n = 0
    for it in data.get("items", []) or []:
        try:
            title = (it.get("title") or "").strip()
            qi = it.get("questionItem")
            qgi = it.get("questionGroupItem")
            if qi:
                q = qi.get("question", {}) or {}
                opts: List[str] = []
                qtype = None
                if "choiceQuestion" in q:
                    cq = q["choiceQuestion"]
                    qtype = _CHOICE_TYPE.get(cq.get("type"), "single")
                    opts = [o.get("value", "") for o in cq.get("options", []) if o.get("value")]
                elif "scaleQuestion" in q:
                    sq = q["scaleQuestion"]
                    qtype = "scale"
                    lo, hi = sq.get("low"), sq.get("high")
                    llab, hlab = sq.get("lowLabel", ""), sq.get("highLabel", "")
                    opts = [f"{lo} {llab}".strip(), f"{hi} {hlab}".strip()]
                elif "textQuestion" in q:
                    qtype = "open"
                if title:
                    n += 1
                    out.append(Question(n=n, text=title, options=[o for o in opts if o], qtype=qtype))
            elif qgi:
                grid = qgi.get("grid", {}) or {}
                cols_cq = grid.get("columns", {}) or {}
                cols = [o.get("value", "") for o in cols_cq.get("options", []) if o.get("value")]
                rows = [((r.get("rowQuestion") or {}).get("title", "")).strip()
                        for r in (qgi.get("questions", []) or [])]
                if title:
                    n += 1
                    out.append(Question(n=n, text=title, options=cols,
                                        rows=[r for r in rows if r], qtype="matrix"))
        except (AttributeError, TypeError):
            continue
    return out
