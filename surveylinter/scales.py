"""Response-option / scale rules. Operate on ``Question.options``."""
from __future__ import annotations

import re
from typing import List

from .model import Finding, Question, HIGH, MED, LOW
from .lexicons import Lexicon
from ._util import L


def _mk(sev, code, name, msg, fix=None) -> Finding:
    return Finding(severity=sev, code=code, name=name, message=msg, fix=fix, target="scale")


def _joined(q: Question) -> str:
    return " , ".join(q.options)


def overlapping_ranges(q: Question, lex: Lexicon) -> List[Finding]:
    s = _joined(q)
    nums = [(int(a), int(b)) for a, b in re.findall(r"(\d+)\s*[-–—]\s*(\d+)", s)]
    for i in range(len(nums) - 1):
        if nums[i][1] >= nums[i + 1][0]:
            a, b, c, d = nums[i][0], nums[i][1], nums[i + 1][0], nums[i + 1][1]
            return [_mk(HIGH, "overlapping_ranges", L(lex, "Overlapping ranges", "区间重叠"),
                        L(lex, f"{a}–{b} and {c}–{d} overlap — a respondent at the boundary can pick two; use mutually exclusive ranges",
                          f"{a}–{b} 与 {c}–{d} 区间重叠——边界值可同时落入两档；改为互斥区间"))]
    return []


def unbalanced_scale(q: Question, lex: Lexicon) -> List[Finding]:
    s = _joined(q).lower()
    pos, neg = len(lex.has(s, lex.pos_anchors)), len(lex.has(s, lex.neg_anchors))
    if pos and neg and abs(pos - neg) >= 2:
        skew = (L(lex, "positive", "正向") if pos > neg else L(lex, "negative", "负向"))
        return [_mk(HIGH, "unbalanced_scale", L(lex, "Unbalanced scale", "量表不平衡"),
                    L(lex, f"{pos} positive vs {neg} negative anchors — responses will skew {skew}; balance them",
                      f"{pos} 个正向 vs {neg} 个负向锚点——结果会偏{skew}；请对称化"))]
    return []


def missing_neutral(q: Question, lex: Lexicon) -> List[Finding]:
    parts = [p for p in q.options if p.strip()]
    s = _joined(q).lower()
    pos, neg = len(lex.has(s, lex.pos_anchors)), len(lex.has(s, lex.neg_anchors))
    if 4 <= len(parts) <= 11 and (pos or neg) and len(parts) % 2 == 0:
        if not lex.has(s, lex.neutral_tokens):
            return [_mk(MED, "missing_neutral", L(lex, "No neutral midpoint", "缺少中间项"),
                        L(lex, f"{len(parts)}-point scale with no neutral/'no opinion' — forces a side; use an odd count or add a neutral option",
                          f"{len(parts)} 点量表且无中立/「无意见」项——迫使受访者选边；改为奇数点或加中立项"))]
    return []


def too_many_points(q: Question, lex: Lexicon) -> List[Finding]:
    parts = [p for p in q.options if p.strip()]
    s = _joined(q).lower()
    if len(parts) > 7 and (lex.has(s, lex.pos_anchors) or lex.has(s, lex.neg_anchors)):
        return [_mk(LOW, "too_many_points", L(lex, "Too many points", "点数过多"),
                    L(lex, f"{len(parts)} options — beyond ~7 points adds noise, not precision",
                      f"{len(parts)} 个选项——超过约 7 点只增加噪声、无助精度"))]
    return []


def non_exhaustive(q: Question, lex: Lexicon) -> List[Finding]:
    parts = [p for p in q.options if p.strip()]
    s = _joined(q).lower()
    is_attitudinal = bool(lex.has(s, lex.pos_anchors) or lex.has(s, lex.neg_anchors))
    is_numeric = bool(re.search(r"\d+\s*[-–—]\s*\d+", s))
    if (q.qtype in (None, "single", "multi")) and 3 <= len(parts) <= 12 \
            and not is_attitudinal and not is_numeric:
        if not lex.has(s, lex.other_tokens):
            return [_mk(MED, "non_exhaustive", L(lex, "Possibly non-exhaustive", "选项可能不穷尽"),
                        L(lex, "a categorical list with no 'Other' / 'None of these' — add an escape option if the list may not cover everyone",
                          "分类选项缺少「其他」/「以上都不是」——若列表未必覆盖所有人，请加兜底项"))]
    return []


SCALE_RULES = [overlapping_ranges, unbalanced_scale, missing_neutral, too_many_points, non_exhaustive]
