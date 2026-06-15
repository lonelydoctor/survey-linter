#!/usr/bin/env python3
"""
survey-linter — deterministic question-quality checks for surveys/questionnaires.

The trust anchor of the skill: every finding here is a concrete, rule-based match
the user can verify against their own wording. No network, no LLM, no dependencies.

Usage:
    python lint_survey.py questions.txt          # one item per line (md bullets/numbers ok)
    python lint_survey.py questions.txt --json    # machine-readable output
    cat questions.txt | python lint_survey.py -    # read from stdin
"""
import sys, re, json

# ---------- lexicons ----------
LOADED = [
    "amazing","awesome","excellent","terrible","awful","horrible","wonderful","fantastic",
    "obviously","simply","just","surely","clearly","of course","everyone knows",
    "fail to","don't you agree","do you agree","wouldn't you say","isn't it true",
    "best","worst","greatest","incredible","outstanding","poor","useless",
]
ABSOLUTES = ["always","never","all","none","every","everyone","everybody","nobody","no one","any time","each and every"]
VAGUE = ["often","regularly","sometimes","occasionally","frequently","rarely","usually","many","few","several","a lot","some","most"]
PRESUPPOSITION = ["how much do you love","how much do you enjoy","why is","why do you like","what do you love","how great"]
SENSITIVE = ["age","income","salary","earn","race","ethnic","religion","religious","health","medical","disability",
             "sexual","gender identity","political","immigration","citizenship","weight","pregnan","criminal","arrest"]
JARGON_OK = {"NPS","CSAT","CES","FAQ","CEO","CTO","HR","IT","AI","USA","UK","ID","URL","API","OK","TV","PDF"}  # tolerated acronyms

NEUTRAL_TOKENS = ["neutral","neither","no opinion","not sure","prefer not","n/a","na","don't know","dont know","unsure"]
POS_ANCHORS = ["excellent","very good","good","satisfied","very satisfied","extremely satisfied","agree","strongly agree",
               "likely","very likely","always","often","great","somewhat satisfied","somewhat agree"]
NEG_ANCHORS = ["poor","very poor","bad","very bad","dissatisfied","very dissatisfied","extremely dissatisfied","disagree",
               "strongly disagree","unlikely","very unlikely","never","rarely","terrible","somewhat dissatisfied","somewhat disagree"]

SEV = {"high": "🔴", "med": "🟠", "low": "🟡"}

def clean(line):
    s = line.strip()
    s = re.sub(r'^\s*(?:[-*•]|\d+[.)]|Q\d+[.):]?)\s*', '', s, flags=re.I)  # strip bullets / numbering / Q1.
    return s.strip()

def has_word(text, words):
    t = " " + re.sub(r'[^\w\s/'+re.escape("'")+r']', ' ', text.lower()) + " "
    hits = []
    for w in words:
        if re.search(r'(?<!\w)' + re.escape(w) + r'(?!\w)', t):
            hits.append(w)
    return hits

def is_scale_line(s):
    # a response-option / scale line: comma- or pipe-separated short anchors, or a numeric range
    if re.search(r'\b\d+\s*[-–]\s*\d+\b', s):
        return True
    parts = re.split(r'[,/|]| - ', s)
    return len(parts) >= 3 and len(s) < 160 and not s.endswith("?")

def check_question(q):
    findings = []
    low = q.lower()
    words = q.split()

    # double-barreled: conjunction joining two askables, or a slash, or two '?'
    if q.count("?") > 1:
        findings.append(("high","Double-barreled","contains more than one question — split into separate items"))
    if re.search(r'\b(\w+)\s+and\s+(\w+)\b', low) and ("?" in q or len(words) > 6):
        # crude: 'and' joining two adjectives/nouns inside one ask
        if not re.search(r'\bterms and conditions\b|\bback and forth\b', low):
            findings.append(("high","Double-barreled","'and' bundles two attributes/topics; a respondent may feel differently about each — split them"))
    if re.search(r'\w+/\w+', q) and "/" not in "n/a" and not re.search(r'https?://', low):
        findings.append(("med","Possibly double-barreled","a slash ('/') often hides two separate things — confirm it's one concept"))

    for w in has_word(low, ABSOLUTES):
        findings.append(("med","Absolute term",f"'{w}' forces an all-or-nothing answer; few things are truly {w} — soften or use a frequency scale")); break
    for w in has_word(low, VAGUE):
        findings.append(("med","Vague quantifier",f"'{w}' means different things to different people; use concrete ranges (e.g., '1–2 times/week')")); break
    loaded_hits = has_word(low, LOADED)
    if loaded_hits:
        findings.append(("high","Leading / loaded",f"loaded wording ({', '.join(loaded_hits[:3])}) pushes the respondent toward an answer — use neutral phrasing"))
    for p in PRESUPPOSITION:
        if p in low:
            findings.append(("high","Presupposition",f"'{p}…' assumes a positive attitude; ask whether, then how much")); break

    # double negative
    negs = len(re.findall(r"\b(no|not|never|none|n't|cannot|can't|without|un\w+|dis\w+)\b", low))
    if negs >= 2:
        findings.append(("med","Double negative","two or more negatives make the item hard to parse — rephrase positively"))

    # sensitive
    sens = has_word(low, SENSITIVE)
    if sens:
        findings.append(("low","Sensitive topic",f"asks about {sens[0]} — make it optional and add a 'Prefer not to say' option"))

    # length
    if len(words) > 25:
        findings.append(("low","Too long",f"{len(words)} words — long items increase misreading; tighten to one clear ask"))

    # jargon / undefined acronyms
    acro = [w.strip(".,?:;") for w in words if re.fullmatch(r'[A-Z]{2,5}s?', w.strip(".,?:;"))]
    acro = [a for a in acro if a.upper() not in JARGON_OK]
    if acro:
        findings.append(("low","Possible jargon",f"undefined acronym(s): {', '.join(sorted(set(acro))[:3])} — spell out on first use"))

    return findings

def check_scale(s):
    findings = []
    low = s.lower()
    # numeric overlap e.g. 0-5, 5-10
    ranges = re.findall(r'(\d+)\s*[-–]\s*(\d+)', s)
    nums = [(int(a),int(b)) for a,b in ranges]
    for i in range(len(nums)-1):
        if nums[i][1] >= nums[i+1][0]:
            findings.append(("high","Overlapping ranges",f"{nums[i][0]}–{nums[i][1]} and {nums[i+1][0]}–{nums[i+1][1]} overlap — a respondent at the boundary can pick two")); break
    # balance
    pos = len(has_word(low, POS_ANCHORS)); neg = len(has_word(low, NEG_ANCHORS))
    if pos and neg and abs(pos-neg) >= 2:
        findings.append(("high","Unbalanced scale",f"{pos} positive vs {neg} negative anchors — responses will skew {'positive' if pos>neg else 'negative'}; balance them"))
    # neutral midpoint on even-count attitudinal scales
    parts = [p.strip() for p in re.split(r'[,/|]', s) if p.strip()]
    if 4 <= len(parts) <= 11 and (pos or neg):
        if not has_word(low, NEUTRAL_TOKENS) and len(parts) % 2 == 0:
            findings.append(("med","No neutral midpoint",f"{len(parts)}-point scale with no neutral/'no opinion' — forces a side; use an odd count or add a neutral option"))
    if len(parts) > 7 and (pos or neg):
        findings.append(("low","Too many points",f"{len(parts)} options — beyond ~7 points adds noise, not precision"))
    return findings

def lint(lines):
    items, results, qn = [], [], 0
    for raw in lines:
        s = clean(raw)
        if not s:
            continue
        if is_scale_line(s) and items:
            sc = check_scale(s)
            if sc:
                results.append({"attached_to": qn, "text": s, "type": "scale", "findings": sc})
            continue
        qn += 1
        items.append(s)
        results.append({"n": qn, "text": s, "type": "question", "findings": check_question(s)})
    return results

def render(results):
    qs = [r for r in results if r["type"] == "question"]
    allf = [f for r in results for f in r["findings"]]
    high = sum(1 for s,_,_ in allf if s == "high")
    verdict = "ship-ready" if not allf else ("needs work" if high else "minor fixes")
    out = [f"SURVEY LINT REPORT (deterministic checks)",
           f"Verdict: {verdict} — {len(qs)} questions, {len(allf)} issues ({high} high)\n"]
    for r in results:
        if not r["findings"]:
            if r["type"] == "question":
                out.append(f'Q{r["n"]}. "{r["text"]}"\n  ✅ no deterministic issues\n')
            continue
        head = (f'Q{r["n"]}. "{r["text"]}"' if r["type"]=="question"
                else f'   ↳ scale: "{r["text"]}"')
        out.append(head)
        for sev, name, why in r["findings"]:
            out.append(f'  {SEV[sev]} {name} — {why}')
        out.append("")
    out.append("Every flag above is rule-based and points to exact wording — verify each against your question.")
    return "\n".join(out)

def main():
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    src = args[0] if args else "-"
    data = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    results = lint(data.splitlines())
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(render(results))

if __name__ == "__main__":
    main()
