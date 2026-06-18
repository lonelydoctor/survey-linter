"""Question-level (wording) rules.

Each rule is a pure function ``(Question, Lexicon) -> list[Finding]`` registered
in ``QUESTION_RULES``. Rules read only the lexicon for language-specific cues, so
the same logic serves every language. Messages are localized via ``L``.
"""
from __future__ import annotations

import re
from typing import List

from .model import Finding, Question, HIGH, MED, LOW
from .lexicons import Lexicon
from ._util import L

WHITELIST_AND = ("terms and conditions", "back and forth", "friends and family",
                 "research and development", "black and white", "q&a", "pros and cons")


def _mk(sev, code, name, msg, fix=None, target="question") -> Finding:
    return Finding(severity=sev, code=code, name=name, message=msg, fix=fix, target=target)


def double_barreled(q: Question, lex: Lexicon) -> List[Finding]:
    text, low = q.text, q.text.lower()
    if not lex.cjk and text.count("?") > 1:
        return [_mk(HIGH, "double_barreled", "Double-barreled",
                    "contains more than one question — split into separate items")]
    if lex.cjk:
        hits = [c for c in lex.conjunctions if c in text]
        if hits and lex.length(text) >= 12:
            return [_mk(MED, "double_barreled", "可能的双桶问题",
                        f"出现连接词「{hits[0]}」，可能把两件事合并问；受访者对每件事的感受可能不同——考虑拆开")]
        return []
    if "as well as" in low or (re.search(r"\b\w+\s+and\s+\w+\b", low)
                               and (low.count("?") or len(text.split()) > 6)):
        if not any(w in low for w in WHITELIST_AND):
            return [_mk(HIGH, "double_barreled", "Double-barreled",
                        "a conjunction bundles two attributes/topics; a respondent may feel "
                        "differently about each — split them")]
    return []


def slash_ambiguity(q: Question, lex: Lexicon) -> List[Finding]:
    low = q.text.lower()
    if re.search(r"\w/\w", q.text) and not re.search(r"https?://", low) and "n/a" not in low:
        return [_mk(MED, "slash_ambiguity", L(lex, "Possibly double-barreled", "可能的双桶问题"),
                    L(lex, "a slash ('/') often hides two separate things — confirm it's one concept",
                      "斜杠「/」常把两个概念合在一起——确认它确实是同一件事"))]
    return []


def leading_loaded(q: Question, lex: Lexicon) -> List[Finding]:
    hits = lex.has(q.text, lex.loaded)
    if hits:
        joined = ", ".join(hits[:3])
        return [_mk(HIGH, "leading_loaded", L(lex, "Leading / loaded", "诱导 / 负载性措辞"),
                    L(lex, f"loaded wording ({joined}) pushes the respondent toward an answer — use neutral phrasing",
                      f"负载性措辞（{joined}）会把受访者推向某个答案——改用中性表达"))]
    return []


def presupposition(q: Question, lex: Lexicon) -> List[Finding]:
    for p in lex.presupposition:
        if p.lower() in q.text.lower():
            return [_mk(HIGH, "presupposition", L(lex, "Presupposition", "预设立场"),
                        L(lex, f"'{p}…' assumes an attitude that isn't established; ask whether, then how much",
                          f"「{p}…」预设了某种态度；应先问“是否”，再问“程度”"))]
    return []


def absolute_term(q: Question, lex: Lexicon) -> List[Finding]:
    hits = lex.has(q.text, lex.absolutes)
    if hits:
        w = hits[0]
        return [_mk(MED, "absolutes", L(lex, "Absolute term", "绝对化措辞"),
                    L(lex, f"'{w}' forces an all-or-nothing answer; few things are truly {w} — soften or use a frequency scale",
                      f"「{w}」迫使非此即彼的回答；很少有事情真的「{w}」——弱化措辞或改用频率量表"))]
    return []


def vague_quantifier(q: Question, lex: Lexicon) -> List[Finding]:
    hits = lex.has(q.text, lex.vague)
    if hits:
        w = hits[0]
        return [_mk(MED, "vague_quantifier", L(lex, "Vague quantifier", "模糊量词"),
                    L(lex, f"'{w}' means different things to different people; use concrete ranges (e.g., '1–2 times/week')",
                      f"「{w}」对每个人含义不同；改用具体区间（如「每周 1–2 次」）"))]
    return []


def double_negative(q: Question, lex: Lexicon) -> List[Finding]:
    low = q.text.lower()
    if lex.cjk:
        pat = "|".join(sorted((re.escape(n) for n in lex.negations), key=len, reverse=True))
        negs = len(re.findall(pat, low))
    else:
        negs = len(re.findall(r"\b(no|not|never|none|n't|cannot|can't|without|un\w+|dis\w+)\b", low))
    if negs >= 2:
        return [_mk(MED, "double_negative", L(lex, "Double negative", "双重否定"),
                    L(lex, "two or more negatives make the item hard to parse — rephrase positively",
                      "两个及以上的否定词使题目难以理解——改用正向表述"))]
    return []


def ambiguous_referent(q: Question, lex: Lexicon) -> List[Finding]:
    if lex.cjk:
        return []  # CJK pronoun-ambiguity needs segmentation; left to the judgment layer
    if re.match(r"^\s*(it|they|them|this|that|these|those)\b", q.text.lower()):
        return [_mk(MED, "ambiguous_referent", "Ambiguous referent",
                    "opens with a pronoun with no clear antecedent — name the thing it refers to")]
    return []


def recall_burden(q: Question, lex: Lexicon) -> List[Finding]:
    for pat in lex.recall_patterns:
        if re.search(pat, q.text, flags=re.I):
            return [_mk(MED, "recall_burden", L(lex, "Recall burden", "回忆负担"),
                        L(lex, "asks respondents to recall counts over a long window — memory is unreliable; "
                               "shorten the window or offer ranges / 'don't recall'",
                          "要求回忆较长时间窗内的次数——记忆不可靠；缩短时间窗或提供区间/「记不清」选项"))]
    return []


def sensitive_topic(q: Question, lex: Lexicon) -> List[Finding]:
    hits = lex.has(q.text, lex.sensitive)
    if hits:
        return [_mk(LOW, "sensitive_topic", L(lex, "Sensitive topic", "敏感话题"),
                    L(lex, f"asks about {hits[0]} — make it optional and add a 'Prefer not to say' option",
                      f"涉及「{hits[0]}」——设为可选并增加「不愿透露」选项"))]
    return []


def dynamic_piped_text(q: Question, lex: Lexicon) -> List[Finding]:
    if re.search(r"\$\{[^}]+\}|\{\{[^}]+\}\}|\[(?:Field|Question|Q)\s*[-:]?\s*\d+\]", q.text):
        return [_mk(LOW, "piped_text", L(lex, "Piped / dynamic text", "管道/动态文本"),
                    L(lex, "contains piped text (e.g. ${...} / {{...}}) — verify it always resolves and reads naturally",
                      "包含管道文本（如 ${...} / {{...}}）——确认它总能正确替换且读起来通顺"))]
    return []


def jargon_acronym(q: Question, lex: Lexicon) -> List[Finding]:
    acro = re.findall(r"\b[A-Z]{2,5}s?\b", q.text)
    ok = {x.upper() for x in lex.jargon_ok}
    acro = [a for a in acro if a.upper() not in ok and a.upper().rstrip("S") not in ok]
    if acro:
        joined = ", ".join(sorted(set(acro))[:3])
        return [_mk(LOW, "jargon", L(lex, "Possible jargon", "可能的术语/缩写"),
                    L(lex, f"undefined acronym(s): {joined} — spell out on first use",
                      f"未解释的缩写：{joined}——首次出现时写全称"))]
    return []


def too_long(q: Question, lex: Lexicon) -> List[Finding]:
    n = lex.length(q.text)
    if n > lex.length_max:
        unit = "字" if lex.cjk else "words"
        return [_mk(LOW, "too_long", L(lex, "Too long", "题目过长"),
                    L(lex, f"{n} {unit} — long items increase misreading; tighten to one clear ask",
                      f"{n} {unit}——过长易被误读；精简为一个清晰的提问"))]
    return []


QUESTION_RULES = [
    double_barreled, slash_ambiguity, leading_loaded, presupposition,
    absolute_term, vague_quantifier, double_negative, ambiguous_referent,
    recall_burden, sensitive_topic, dynamic_piped_text, jargon_acronym, too_long,
]
