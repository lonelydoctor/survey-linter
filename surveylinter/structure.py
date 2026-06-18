"""Whole-instrument (structural) rules: priming, sensitive placement, fatigue."""
from __future__ import annotations

import re
from typing import List

from .model import Finding, Question, MED, LOW
from .lexicons import Lexicon
from ._util import L


def run(questions: List[Question], lex: Lexicon) -> List[Finding]:
    out: List[Finding] = []
    general_pat = (r"总体|整体|总的来说|愿意推荐|推荐给" if lex.cjk
                   else r"\boverall\b|\brecommend\b|\bin general\b|\bnet promoter\b")
    praise_idx = general_idx = None
    for i, q in enumerate(questions):
        if praise_idx is None and lex.has(q.text, lex.loaded):
            praise_idx = i
        if general_idx is None and re.search(general_pat, q.text.lower()):
            general_idx = i
    if praise_idx is not None and general_idx is not None and praise_idx < general_idx:
        pn, gn = questions[praise_idx].n, questions[general_idx].n
        out.append(Finding(MED, "order_priming", L(lex, "Order / priming", "题序 / priming"),
                   L(lex, f"a flattering/branded item (Q{pn}) appears before the general/overall item (Q{gn}) — "
                          f"this primes responses; put the general question first",
                     f"带正面/品牌色彩的题目(Q{pn})出现在总体/推荐题(Q{gn})之前——会对总体判断造成 priming；把总体题放前面"),
                   target="structure"))

    half = max(1, len(questions) // 2)
    for q in questions[:half]:
        if lex.has(q.text, lex.sensitive):
            out.append(Finding(LOW, "sensitive_placement", L(lex, "Sensitive placement", "敏感题位置"),
                       L(lex, f"sensitive item Q{q.n} appears early — place sensitive questions late and make them optional",
                         f"敏感题 Q{q.n} 出现在前半部分——敏感题应放在靠后并设为可选"),
                       target="structure"))
            break

    if len(questions) > 30:
        out.append(Finding(LOW, "length_fatigue", L(lex, "Length / fatigue", "问卷过长 / 疲劳"),
                   L(lex, f"{len(questions)} questions — long surveys lower data quality near the end; cut to what you'll act on",
                     f"共 {len(questions)} 题——问卷过长会降低末尾数据质量；精简到你真正会用的问题"),
                   target="structure"))
    return out
