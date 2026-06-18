# Worked example

Input: `examples/sample_survey.txt` (a deliberately flawed customer survey).
Below is what the skill produces — the deterministic pass (the engine, with a
reproducible score) plus the judgment layer and rewrites. A Chinese example runs
the same way: `python scripts/lint_survey.py examples/sample_survey_zh.txt --lang zh`.

---

## 1) Deterministic pass (verbatim engine output)

```
SURVEY LINT REPORT (deterministic)  [lang: en]
Score: 6/100  (grade F)  —  verdict: needs work
Issues: 11  (🔴 6  🟠 3  🟡 2)  across 8 questions
Scoring: 100 − (🔴6×12 + 🟠3×6 + 🟡2×2) = 6

Q1. "How satisfied are you with our fast and friendly support?"
  🔴 Double-barreled — a conjunction bundles two attributes/topics; split them
Q2. "Don't you agree that our amazing app is easy to use?"
  🔴 Leading / loaded — loaded wording (amazing, don't you agree) pushes toward an answer
Q3. "How often do you regularly use the product?"
  🟠 Vague quantifier — 'often' is not comparable across respondents
   ↳ scale: "Excellent, Very Good, Good, Satisfied, Poor"
     🔴 Unbalanced scale — 4 positive vs 1 negative anchors → skews positive
Q4. "What is your annual income?"
  🟡 Sensitive topic — make optional + add 'Prefer not to say'
Q5. "Rate our service: 0-5, 5-10"
     🔴 Overlapping ranges — 5 belongs to two buckets
Q6. "Would you not be unwilling to recommend us?"
  🟠 Double negative — hard to parse; rephrase positively
Q7. "How much do you love our new NPS dashboard and CSAT reporting?"
  🔴 Double-barreled — bundles "NPS dashboard" and "CSAT reporting"
  🔴 Presupposition — "how much do you love" assumes the attitude
Q8. "How likely are you to recommend us?"
  ✅ no deterministic issues

Structural:
  🟠 Order / priming — flattering Q2 precedes the general item (Q6); put the general question first
  🟡 Sensitive placement — Q4 (income) appears early; place sensitive items late
```

Every flag above is rule-based and points to exact wording — verifiable line by line.
The score is the printed formula, not a black box.

## 2) Judgment layer + rewrites (added by the skill)

**Q1.** 🔴 Double-barreled — "fast" and "friendly" are two things; someone who finds
support fast but curt can't answer honestly.
✅ Split:
  - "How satisfied are you with the **speed** of our support?" + balanced 5-pt scale
  - "How satisfied are you with the **friendliness** of our support?" + balanced 5-pt scale

**Q2.** 🔴 Leading — "Don't you agree" + "amazing" both push toward yes.
✅ "How easy or difficult is the app to use?" (Very easy … Very difficult)

**Q3.** 🟠 Vague + 🔴 unbalanced scale.
✅ "In the past 7 days, on how many days did you use the product?" (0–7); replace the
scale with Very satisfied / Satisfied / Neutral / Dissatisfied / Very dissatisfied.

**Q4.** 🟡 Sensitive — make optional, use ranges, add "Prefer not to say"; move near the end.

**Q5.** 🔴 Overlapping ranges — "5" fits two buckets.
✅ 0–3 / 4–6 / 7–8 / 9–10, or a single labeled 0–10 scale.

**Q6.** 🟠 Double negative.
✅ "How likely are you to recommend us?" (0–10 — the NPS standard).

**Q7.** 🔴 Double-barreled + 🔴 presupposition.
✅ Split + neutralize: "How useful is the NPS dashboard?" / "How useful is the CSAT
reporting?" (Very useful … Not at all useful).

**Q8.** ✅ Clean; scale is balanced with a neutral midpoint.

**Structural:** put the general recommendation/satisfaction question early to avoid
priming, and place the income question last (optional).

*The 🔴/🟠/🟡 flags and the score come from the engine and are verifiable; the
"useful vs love", priming, and recall judgments are explained so you can decide.*
