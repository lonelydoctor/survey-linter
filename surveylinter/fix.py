"""Deterministic rewrite suggestions.

Only proposes fixes that follow mechanically from a finding (balanced scales,
exclusive ranges, optional sensitive items, split templates). Wording rewrites
that need human judgment are described, not fabricated — the skill's judgment
layer produces the final prose.
"""
from __future__ import annotations

import re
from typing import List, Optional

from .model import Report, Question, Finding, SEV_EMOJI
from .lexicons import get_lexicon, Lexicon
from ._util import L


def _balanced_scale(lex: Lexicon, anchors_lower: str) -> List[str]:
    if ("满意" if lex.cjk else "satisf") in anchors_lower:
        return (["非常满意", "满意", "一般", "不满意", "非常不满意"] if lex.cjk
                else ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"])
    if ("同意" if lex.cjk else "agree") in anchors_lower:
        return (["非常同意", "同意", "中立", "不同意", "非常不同意"] if lex.cjk
                else ["Strongly agree", "Agree", "Neither", "Disagree", "Strongly disagree"])
    return (["非常好", "好", "一般", "差", "非常差"] if lex.cjk
            else ["Very good", "Good", "Neutral", "Poor", "Very poor"])


def _fix_ranges(joined: str) -> str:
    nums = [(int(a), int(b)) for a, b in re.findall(r"(\d+)\s*[-–—]\s*(\d+)", joined)]
    fixed = []
    for i, (lo, hi) in enumerate(nums):
        if i + 1 < len(nums) and hi >= nums[i + 1][0]:
            hi = nums[i + 1][0] - 1
        fixed.append(f"{lo}–{hi}")
    return ", ".join(fixed)


def suggestion(q: Question, f: Finding, lex: Lexicon) -> Optional[str]:
    code = f.code
    joined = " , ".join(q.options)
    if code == "double_barreled":
        return L(lex, "Split into two items, one topic each — give each its own scale.",
                 "拆成两题，每题只问一件事，各配一套量表。")
    if code in ("unbalanced_scale", "missing_neutral"):
        return L(lex, "Use a balanced odd-point scale: " + " / ".join(_balanced_scale(lex, joined.lower())),
                 "改用对称的奇数点量表：" + " / ".join(_balanced_scale(lex, joined.lower())))
    if code == "overlapping_ranges":
        return L(lex, "Use mutually exclusive ranges: " + _fix_ranges(joined),
                 "改用互斥区间：" + _fix_ranges(joined))
    if code == "sensitive_topic":
        return L(lex, 'Make it optional, add "Prefer not to say", and place it late in the survey.',
                 "设为可选、增加「不愿透露」选项，并放到问卷靠后位置。")
    if code in ("vague_quantifier", "absolutes"):
        return L(lex, "Replace with a concrete range (e.g. 'In the past 7 days, on how many days…').",
                 "改用具体区间（如「过去 7 天里有几天…」）。")
    if code == "double_negative":
        return L(lex, "Rephrase positively (e.g. 'How likely are you to…?').",
                 "改为正向表述（如「你有多大可能…？」）。")
    if code in ("leading_loaded", "presupposition"):
        return L(lex, "Remove evaluative wording; ask neutrally — whether first, then how much.",
                 "去掉评价性措辞，中性提问——先问是否，再问程度。")
    if code == "non_exhaustive":
        return L(lex, 'Add an "Other (please specify)" / "None of these" option.',
                 "增加「其他（请注明）」/「以上都不是」选项。")
    if code == "recall_burden":
        return L(lex, "Shorten the recall window or offer ranges / a 'don't recall' option.",
                 "缩短回忆时间窗，或提供区间/「记不清」选项。")
    return None


def render_fixes(report: Report) -> str:
    lex = get_lexicon(report.lang)
    out = [L(lex, "SUGGESTED REVISIONS (deterministic)", "建议修订（确定性规则）"), ""]
    any_fix = False
    for q in report.questions:
        seen, sugg = set(), []
        for f in q.findings:
            s = suggestion(q, f, lex)
            if s and (f.code, s) not in seen:
                seen.add((f.code, s))
                sugg.append((f, s))
        if not sugg:
            continue
        any_fix = True
        out.append(f'Q{q.n}. "{q.text}"')
        if q.options:
            out.append(L(lex, f"   current options: {', '.join(q.options)}",
                         f"   当前选项：{', '.join(q.options)}"))
        for f, s in sugg:
            out.append(f"  {SEV_EMOJI[f.severity]} {f.name} → {s}")
        out.append("")
    if not any_fix:
        out.append(L(lex, "No deterministic revisions needed.", "无需确定性修订。"))
    else:
        out.append(L(lex, "These are mechanical suggestions; keep your intent and let the judgment layer finalize prose.",
                     "以上为机械化建议；请保留你的本意，最终措辞交由判断层润色。"))
    return "\n".join(out)
