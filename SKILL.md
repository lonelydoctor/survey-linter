---
name: survey-linter
description: "Audit a survey or questionnaire for question-quality problems before it is sent — flags leading, loaded, double-barreled, double-negative, and absolute wording; vague quantifiers; jargon; unbalanced or overlapping rating scales; missing neutral / 'Prefer not to say' options; sensitive questions without an opt-out; and question-order bias — then rewrites each flagged item. Use whenever the user shares or is writing a survey, questionnaire, poll, NPS / CSAT / feedback form, market-research instrument, course evaluation, or employee/engagement survey and wants it reviewed, critiqued, de-biased, or 'made better' before launch."
license: MIT
---

# Survey Linter

Most surveys are written by people who are experts in their topic but not in measurement. The result is data that looks fine but is quietly biased — leading questions, double-barreled items, unbalanced scales — and you only find out after you've already collected the responses. This skill reviews a questionnaire **before it ships** and tells the user, item by item, what will bias their data and how to fix it.

The design principle: **the high-confidence problems are caught deterministically (a script), so every flag is concrete and checkable; the judgment calls (is this leading? is this loaded?) are explained, never asserted.** The user can verify every finding against their own question.

## When to use

Trigger when the user shares or is drafting any instrument that collects structured responses: survey, questionnaire, poll, NPS/CSAT/CES, feedback or intake form, market-research study, course or event evaluation, employee/engagement/pulse survey, screener, or quiz. Phrases like "review my survey", "is this a good question", "de-bias my questionnaire", "before I send this form."

## Workflow

1. **Extract the questions.** Parse the user's survey into a clean list of items (strip numbering/bullets). If response options or scales are given, keep them with their question. If the survey is a file, read it; if pasted, use it directly.

2. **Run the deterministic checks.** Run `scripts/lint_survey.py` on the extracted questions. It catches the unambiguous problems (see `references/rule_catalog.md` for the full taxonomy):
   - double-barreled (asks two things at once)
   - absolutes (always / never / all / none / every)
   - double negatives
   - vague quantifiers (often / regularly / sometimes)
   - loaded / leading lexicon and presupposition cues
   - jargon / undefined acronyms
   - over-long items (> ~25 words)
   - sensitive topics (age, income, health, race, religion, etc.) — must be optional with a "Prefer not to say"
   - scale problems when options are present: unbalanced (more positive than negative anchors), even-count scales missing a neutral midpoint, overlapping numeric ranges, too many points
   ```bash
   python scripts/lint_survey.py questions.txt          # text/markdown, one item per line
   python scripts/lint_survey.py questions.txt --json    # machine-readable
   ```

3. **Add the judgment-layer review.** For each item, on top of the script's flags, assess the things a script can't be sure about — subtle leading framing, presupposition, social-desirability pressure, ambiguous referents ("it", "they"), recall difficulty ("how many times last year…"), and **question-order / priming** across the whole instrument. State *why* it biases responses; never just assert "this is leading."

4. **Rewrite every flagged item.** For each problem, give a corrected version. Split double-barreled items into two. Balance scales. Add neutral / N-A / opt-out options where missing. Keep the user's intent and voice.

5. **Output the report** in the format below.

## Output format

Lead with a one-line verdict and a scorecard, then go item by item, then structural issues.

```
SURVEY LINT REPORT
Verdict: <ship-ready | minor fixes | needs work> — N questions, M issues (X high)

Per question:
Q3. "How satisfied are you with our fast, friendly support?"
  🔴 Double-barreled — bundles "fast" and "friendly"; a respondent who finds it fast but unfriendly can't answer.
  🟠 Leading — "fast, friendly" presupposes the support is both.
  ✅ Rewrite:
     • "How satisfied are you with the speed of our support?"  (+ scale)
     • "How satisfied are you with the friendliness of our support?"  (+ scale)

Structural:
  🟠 Scale on Q5 is unbalanced (4 positive anchors, 2 negative) → responses skew positive. Use a balanced 5- or 7-point scale.
  🟡 Sensitive: Q9 asks income — make it optional and add "Prefer not to say."
  🟡 Order: Q2 praises the brand, then Q3 asks overall satisfaction → priming. Put the general question first.
```

Always end by stating that the deterministic flags are verifiable line-by-line and the judgment calls are explained so the user can decide.

## Rules

- Be specific and verifiable: name the exact words/phrase and the mechanism of bias. Never hand-wave.
- Preserve the author's intent and tone in rewrites; don't change what they're measuring.
- Don't invent problems. If a question is clean, say so. A clean bill of health is a valid, valuable result.
- Note locale/translation when relevant (a scale or idiom may not translate cleanly).
- Deep taxonomy and fix patterns live in `references/rule_catalog.md`; report template and good/bad pairs in `assets/`; a full worked example in `examples/`.
