"""Render a Report as a human-readable text report or JSON."""
from __future__ import annotations

import json
from typing import List

from .model import Report, Finding, SEV_EMOJI, HIGH, MED, LOW
from .lexicons import get_lexicon
from ._util import L

_VERDICT_ZH = {"ship-ready": "可发布", "minor fixes": "小修即可", "needs work": "需要修改"}


def render_human(report: Report) -> str:
    lex = get_lexicon(report.lang)
    sc = report.score
    c = sc.counts
    total = c[HIGH] + c[MED] + c[LOW]
    out: List[str] = [
        L(lex, "SURVEY LINT REPORT (deterministic)", "问卷检查报告（确定性规则）") + f"  [lang: {report.lang}]",
        L(lex, f"Score: {sc.value}/100  (grade {sc.grade})  —  verdict: {sc.verdict}",
          f"得分：{sc.value}/100（等级 {sc.grade}）—— 结论：{_VERDICT_ZH.get(sc.verdict, sc.verdict)}"),
        L(lex, f"Issues: {total}  (🔴 {c[HIGH]}  🟠 {c[MED]}  🟡 {c[LOW]})  across {sc.questions} questions",
          f"问题：{total} 个（🔴 {c[HIGH]}  🟠 {c[MED]}  🟡 {c[LOW]}），共 {sc.questions} 题"),
        L(lex, f"Scoring: 100 − (🔴{c[HIGH]}×12 + 🟠{c[MED]}×6 + 🟡{c[LOW]}×2) = {sc.value}",
          f"算分：100 −（🔴{c[HIGH]}×12 + 🟠{c[MED]}×6 + 🟡{c[LOW]}×2）= {sc.value}"),
        "",
    ]
    for q in report.questions:
        qfind = [f for f in q.findings if f.target != "scale"]
        sfind = [f for f in q.findings if f.target == "scale"]
        sect = f"  [{q.section}]" if q.section else ""
        if not qfind and not sfind:
            out.append(f'Q{q.n}. "{q.text}"{sect}')
            out.append(L(lex, "  ✅ no deterministic issues", "  ✅ 无确定性问题") + "\n")
            continue
        out.append(f'Q{q.n}. "{q.text}"{sect}')
        for f in qfind:
            out.append(f"  {SEV_EMOJI[f.severity]} {f.name} — {f.message}")
        if q.options:
            out.append(L(lex, f'   ↳ scale: "{", ".join(q.options)}"',
                         f'   ↳ 量表/选项："{", ".join(q.options)}"'))
            for f in sfind:
                out.append(f"     {SEV_EMOJI[f.severity]} {f.name} — {f.message}")
        out.append("")
    if report.structure:
        out.append(L(lex, "Structural:", "结构性问题："))
        for f in report.structure:
            out.append(f"  {SEV_EMOJI[f.severity]} {f.name} — {f.message}")
        out.append("")
    out.append(L(
        lex,
        "Every flag is rule-based and points to exact wording — verify each. The judgment layer "
        "(subtle leading/priming/recall) is added by the skill on top of these checks.",
        "每条标记都基于规则、指向具体措辞——请逐条核对。更细的判断（隐性诱导/题序/回忆）由技能在此基础上补充。",
    ))
    return "\n".join(out)


def render_json(report: Report) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
