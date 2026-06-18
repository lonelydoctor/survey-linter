# Rule catalog — what biases survey data and how to fix it

Reference for both the deterministic engine and the judgment layer. Severity:
🔴 high (will distort results), 🟠 medium (likely distortion), 🟡 low (hygiene).

Each rule has a stable **code** you can use in `.surveylinterrc` to `disable` it or
override its `severity`. Rules read language-specific cues from the lexicon, so they
apply in every supported language (English, 简体中文).

## Wording rules

| code | rule | sev | why it biases data → fix |
|---|---|---|---|
| `double_barreled` | Double-barreled | 🔴 | Asks two things at once ("fast *and* friendly"). A respondent who feels differently about each can't answer. *Split into one item per attribute.* |
| `leading_loaded` | Leading / loaded | 🔴 | Wording signals the "right" answer ("*amazing*", "*don't you agree*"). Inflates agreement. *Strip evaluative adjectives and agreement cues.* |
| `presupposition` | Presupposition | 🔴 | Assumes something not established ("How much do you *love* X?"). *Ask whether, then how much.* |
| `absolutes` | Absolutes | 🟠 | "always / never / all / none" force all-or-nothing. *Use a frequency scale or soften.* |
| `vague_quantifier` | Vague quantifier | 🟠 | "often / regularly / usually" mean different things to each person → not comparable. *Use concrete ranges.* |
| `double_negative` | Double negative | 🟠 | "would you *not* be *unwilling*…" — high misread rate. *Phrase positively.* |
| `recall_burden` | Recall burden | 🟠 | "how many times in the last 12 months…" — memory is unreliable. *Shorten the window or offer ranges / "don't recall".* |
| `ambiguous_referent` | Ambiguous referent | 🟠 | Opens with "it / they / this" with no antecedent. *Name the thing.* |
| `slash_ambiguity` | Slash ambiguity | 🟠 | A slash often hides two concepts ("price/value"). *Confirm it's one concept.* |
| `piped_text` | Piped / dynamic text | 🟡 | `${...}` / `{{...}}` may not resolve or may read oddly. *Verify it always resolves.* |
| `jargon` | Jargon / acronym | 🟡 | Terms only insiders know. *Spell out on first use.* |
| `too_long` | Too long | 🟡 | Long items (> ~25 words / ~45 CJK chars) raise misreading. *One clear ask.* |

## Response-option & scale rules

| code | rule | sev | why → fix |
|---|---|---|---|
| `unbalanced_scale` | Unbalanced scale | 🔴 | More positive than negative anchors (Excellent/Very good/Good/Fair/Poor) pulls responses up. *Equal positive and negative anchors around a midpoint.* |
| `overlapping_ranges` | Overlapping ranges | 🔴 | "0–5, 5–10" — boundary values fit two buckets. *Mutually exclusive ranges (0–4, 5–9, 10+).* |
| `missing_neutral` | No neutral midpoint | 🟠 | Even-point attitude scale with no midpoint forces a side. *Odd-numbered scale or add "No opinion".* |
| `non_exhaustive` | Non-exhaustive options | 🟠 | Categorical pick-one with no "Other" / "None of these". *Add an escape option.* |
| `too_many_points` | Too many points | 🟡 | Beyond ~7 points respondents can't distinguish; adds noise. *5- or 7-point.* |

## Structure (whole instrument)

| code | rule | sev | why → fix |
|---|---|---|---|
| `order_priming` | Order / priming | 🟠 | A flattering/specific item before a general one biases the general answer. *General/overall questions first; randomize where possible.* |
| `sensitive_placement` | Sensitive placement | 🟡 | Sensitive items early drive drop-off. *Place late and make optional.* |
| `length_fatigue` | Length / fatigue | 🟡 | Very long surveys lower data quality near the end. *Cut to the decisions you'll act on.* |

Sensitive *topics* (age, income, health, race, religion, gender identity, political,
immigration, etc.) are flagged per item by `sensitive_topic` 🟡 — make them optional with
a "Prefer not to say".

## Scoring (transparent)

```
Score = 100 − (🔴 high × 12 + 🟠 med × 6 + 🟡 low × 2)   # floored at 0
Grade: A ≥90, B ≥80, C ≥70, D ≥60, else F
Verdict: ship-ready (no findings) · minor fixes (no high) · needs work (any high)
```

The report prints this arithmetic so it is reproducible by hand — there is no hidden model.

## Multilingual notes

- A scale or idiom may not translate cleanly — lint in the survey's own language (`--lang`).
- CJK rules match on distinctive multi-character cues and count length in characters.
- Adding a language is one lexicon file — see `CONTRIBUTING.md`.

## Likert quick-reference

- 5-point agreement: Strongly disagree / Disagree / Neither / Agree / Strongly agree.
- 5-point satisfaction: Very dissatisfied / Dissatisfied / Neither / Satisfied / Very satisfied.
- Keep anchors symmetric, label every point, and keep one scale direction across the survey.

## Methodology

These rules operationalize long-standing survey-methodology guidance on question
wording, response formats, and instrument order (e.g., the questionnaire-design and
total-survey-error literature). The engine encodes the mechanical, checkable parts;
the judgment layer covers the rest and explains, rather than asserts, each call.
