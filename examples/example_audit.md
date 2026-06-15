# Worked example

Input: `examples/sample_survey.txt` (a deliberately flawed customer survey).
Below is what the skill produces — the deterministic pass (from `lint_survey.py`) plus the judgment layer and rewrites.

---

**SURVEY LINT REPORT**
**Verdict: needs work — 7 questions, 10 issues (6 high)**

**Q1. "How satisfied are you with our fast and friendly support?"**
- 🔴 Double-barreled — "fast" and "friendly" are two different things; someone who finds support fast but curt can't answer honestly.
- 🟠 Leading — "fast, friendly" presupposes support is both.
- ✅ Rewrite (split):
  - "How satisfied are you with the **speed** of our support?" + balanced 5-pt scale
  - "How satisfied are you with the **friendliness** of our support?" + balanced 5-pt scale

**Q2. "Don't you agree that our amazing app is easy to use?"**
- 🔴 Leading / loaded — "Don't you agree" + "amazing" both push toward yes.
- ✅ Rewrite: "How easy or difficult is the app to use?" (Very easy … Very difficult)

**Q3. "How often do you regularly use the product?"**
- 🟠 Vague quantifier — "often"/"regularly" mean different things to each person; not comparable.
- ✅ Rewrite: "In the past 7 days, on how many days did you use the product?" (0–7)
- Attached scale "Excellent, Very Good, Good, Satisfied, Poor":
  - 🔴 Unbalanced — 4 positive anchors vs 1 negative → skews positive.
  - ✅ Rewrite: Very satisfied / Satisfied / Neutral / Dissatisfied / Very dissatisfied.

**Q4. "What is your annual income?"**
- 🟡 Sensitive — required income questions drive drop-off and false answers.
- ✅ Rewrite: make optional, use ranges, add "Prefer not to say"; move near the end.

**Q5. "Rate our service: 0-5, 5-10"**
- 🔴 Overlapping ranges — "5" belongs to both buckets.
- ✅ Rewrite: 0–3 / 4–6 / 7–8 / 9–10, or a single labeled 0–10 scale.

**Q6. "Would you not be unwilling to recommend us?"**
- 🟠 Double negative — "not … unwilling" is hard to parse.
- ✅ Rewrite: "How likely are you to recommend us?" (0–10, the NPS standard).

**Q7. "How much do you love our new NPS dashboard and CSAT reporting?"**
- 🔴 Double-barreled — bundles "NPS dashboard" and "CSAT reporting".
- 🔴 Presupposition — "How much do you love" assumes love.
- ✅ Rewrite (split + neutralize):
  - "How useful is the NPS dashboard?" (Very useful … Not at all useful)
  - "How useful is the CSAT reporting?" (Very useful … Not at all useful)

**Q8. "How likely are you to recommend us?"** — ✅ clean; scale is balanced with a neutral midpoint. Tip: the 0–10 form is the NPS standard if you want a comparable benchmark.

**Structural**
- 🟠 Order / priming — Q1–Q2 praise the product before Q8 (overall recommendation). Put the general/overall question early to avoid priming.
- 🟡 Length is fine, but make Q4 optional and place sensitive items last.

*The 🔴/🟠/🟡 flags from `lint_survey.py` are rule-based and point to exact wording — verify each. The order/priming and "useful vs love" judgments are explained so you can decide.*
