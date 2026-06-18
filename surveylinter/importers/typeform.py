"""Parse a Typeform form-definition JSON (the `fields` array)."""
from __future__ import annotations

from typing import List

from ..model import Question


def parse(data) -> List[Question]:
    out: List[Question] = []
    n = 0
    for f in data.get("fields", []) or []:
        try:
            title = (f.get("title") or "").strip()
            if not title:
                continue
            t = f.get("type")
            props = f.get("properties", {}) or {}
            opts: List[str] = []
            qtype = None
            if "choices" in props:
                opts = [c.get("label", "") for c in props["choices"] if c.get("label")]
                qtype = "multi" if props.get("allow_multiple_selection") else "single"
            elif t in ("opinion_scale", "rating", "number"):
                qtype = "scale"
                labels = props.get("labels", {}) or {}
                steps = props.get("steps")
                opts = [labels.get("left", ""), labels.get("center", ""), labels.get("right", "")]
                opts = [o for o in opts if o] or ([f"1..{steps}"] if steps else [])
            elif t in ("yes_no",):
                qtype = "single"
                opts = ["Yes", "No"]
            elif t in ("long_text", "short_text"):
                qtype = "open"
            n += 1
            out.append(Question(n=n, text=title, options=opts, qtype=qtype))
        except (AttributeError, TypeError):
            continue
    return out
