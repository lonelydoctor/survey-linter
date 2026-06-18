---
name: survey-linter
description: "Audit a survey or questionnaire for question-quality problems before it is sent — flags leading, loaded, double-barreled, double-negative, and absolute wording; vague quantifiers; recall burden; jargon; unbalanced, overlapping, or non-exhaustive rating scales; missing neutral / 'Prefer not to say' options; sensitive questions without an opt-out; and question-order bias — then rewrites each flagged item. Works in English and Simplified Chinese, and can import surveys from plain text, Markdown, CSV, Google Forms, Typeform, or Qualtrics (.qsf). Use whenever the user shares or is writing a survey, questionnaire, poll, NPS / CSAT / feedback form, market-research instrument, course evaluation, or employee/engagement survey and wants it reviewed, critiqued, de-biased, or 'made better' before launch."
license: MIT
---

# Survey Linter

Most surveys are written by people who are experts in their topic but not in measurement. The result is data that looks fine but is quietly biased — leading questions, double-barreled items, unbalanced scales — and you only find out after you've already collected the responses. This skill reviews a questionnaire **before it ships** and tells the user, item by item, what will bias their data and how to fix it.

The design principle: **the high-confidence problems are caught deterministically (a rule engine), so every flag is concrete and checkable; the judgment calls (is this leading? is this loaded?) are explained, never asserted.** The user can verify every finding against their own question.

## When to use

Trigger when the user shares or is drafting any instrument that collects structured responses: survey, questionnaire, poll, NPS/CSAT/CES, feedback or intake form, market-research study, course or event evaluation, employee/engagement/pulse survey, screener, or quiz. Phrases like "review my survey", "is this a good question", "de-bias my questionnaire", "before I send this form." Works for English and Simplified Chinese surveys.

## Workflow

1. **Load the survey.** The linter imports many formats automatically — plain text, Markdown, CSV, Google Forms (API JSON), Typeform (form JSON), and Qualtrics (`.qsf`). If the user pasted text, lint it directly; if it's a file, pass the path. Matrix/grid questions and piped text are handled.

2. **Run the deterministic checks.** Run the linter on the survey. It returns a transparent score and one finding per problem, each pointing to exact wording (full taxonomy in `references/rule_catalog.md`):
   - wording: double-barreled, leading/loaded, presupposition, absolutes, vague quantifiers, double negatives, recall burden, ambiguous referent, piped text, jargon, over-long
   - scales: unbalanced, overlapping ranges, missing neutral, too many points, non-exhaustive options
   - structure: order/priming, sensitive placement, fatigue
   ```bash
   python scripts/lint_survey.py questions.txt              # human report + score
   python scripts/lint_survey.py questions.txt --json        # machine-readable
   python scripts/lint_survey.py questions.txt --fix         # deterministic suggested revisions
   python scripts/lint_survey.py survey.qsf --lang zh        # other formats / Chinese
   ```
   Use `--lang zh` (or let it auto-detect) for Chinese surveys. A `.surveylinterrc` can disable rules, override severities, or ignore lines.

3. **Add the judgment-layer review.** On top of the engine's flags, assess what a rule can't be sure about — subtle leading framing, social-desirability pressure, ambiguous referents, recall difficulty, and **question-order / priming** across the whole instrument. State *why* it biases responses; never just assert "this is leading."

4. **Rewrite every flagged item.** `--fix` gives deterministic starting points (balanced scales, exclusive ranges, optional sensitive items, split templates); finalize the prose yourself. Split double-barreled items, balance scales, add neutral / opt-out options. Keep the user's intent and voice (and language).

5. **Output the report** in the format below.

## Output format

Lead with the score and verdict, then go item by item, then structural issues.

```
SURVEY LINT REPORT (deterministic)  [lang: en]
Score: 64/100 (grade C) — verdict: needs work
Issues: 9 (🔴 6  🟠 2  🟡 1) across 8 questions

Q3. "How satisfied are you with our fast, friendly support?"
  🔴 Double-barreled — bundles "fast" and "friendly"; someone who finds it fast but unfriendly can't answer.
  ✅ Rewrite:
     • "How satisfied are you with the speed of our support?"  (+ balanced scale)
     • "How satisfied are you with the friendliness of our support?"  (+ balanced scale)

Structural:
  🟠 Order: Q2 praises the brand before Q3 asks overall satisfaction → priming. Put the general question first.
  🟡 Sensitive: Q9 asks income — make it optional and add "Prefer not to say."
```

Always end by stating that the deterministic flags are verifiable line-by-line, the score is a reproducible formula, and the judgment calls are explained so the user can decide.

## Rules

- Be specific and verifiable: name the exact words/phrase and the mechanism of bias. Never hand-wave.
- Preserve the author's intent, tone, and language in rewrites; don't change what they're measuring.
- Don't invent problems. If a question is clean, say so. A clean bill of health is a valid, valuable result.
- Note locale/translation when relevant (a scale or idiom may not translate cleanly); use `--lang` to match the survey.
- Deep taxonomy and fix patterns live in `references/rule_catalog.md`; report template and good/bad pairs in `assets/`; a worked example in `examples/`.
