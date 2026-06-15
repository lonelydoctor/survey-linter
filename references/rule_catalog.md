# Rule catalog — what biases survey data and how to fix it

Reference for the judgment layer. Each rule: what it is, why it biases data, how to fix. Severity: 🔴 high (will distort results), 🟠 medium (likely distortion), 🟡 low (hygiene).

## Wording

**Double-barreled 🔴** — one item asks about two things ("fast *and* friendly", "price *and* quality"). A respondent who feels differently about each has no honest answer. *Fix:* split into one item per attribute.

**Leading / loaded 🔴** — wording signals the "right" answer ("How *amazing* was…", "*Don't you agree*…", "our *award-winning* product"). Inflates agreement. *Fix:* strip evaluative adjectives and agreement cues; ask neutrally.

**Presupposition 🔴** — assumes something not established ("How much do you *love* X?", "*Why* is X better?"). *Fix:* ask the yes/no or attitude first, then the degree.

**Absolutes 🟠** — "always / never / all / none / every". Forces all-or-nothing; people round to the middle or refuse. *Fix:* use a frequency scale or soften.

**Vague quantifiers 🟠** — "often / regularly / sometimes / usually". Each respondent defines them differently, so answers aren't comparable. *Fix:* concrete ranges ("1–2 times per week").

**Double negative 🟠** — "would you *not* be *unwilling*…". High misread rate. *Fix:* phrase positively.

**Ambiguous referent 🟠** — "it / they / this" with no clear antecedent. *Fix:* name the thing.

**Recall burden 🟠** — "how many times in the last 12 months…". Memory is unreliable; people guess. *Fix:* shorten the window or use ranges/"don't recall".

**Jargon / undefined acronym 🟡** — terms only insiders know. Non-experts guess or drop off. *Fix:* spell out / define on first use.

**Too long 🟡** — > ~25 words. Misreading rises with length. *Fix:* one clear ask.

## Response options & scales

**Unbalanced scale 🔴** — more positive than negative anchors (Excellent/Very Good/Good/Fair/Poor is 3 pos, 1 neutral, 1 neg). Pulls responses positive. *Fix:* equal positive and negative anchors around a midpoint.

**Overlapping ranges 🔴** — "0–5, 5–10". Boundary values fit two buckets. *Fix:* mutually exclusive ranges ("0–4, 5–9, 10+").

**Missing neutral / forced choice 🟠** — even-point attitude scale with no midpoint forces a side. *Fix:* odd-numbered scale (5 or 7) or add "No opinion". (Sometimes forcing is intentional — note the tradeoff.)

**Too many points 🟡** — beyond ~7 points respondents can't distinguish; adds noise. *Fix:* 5- or 7-point.

**Non-exhaustive options 🟠** — no "Other" / "None of these" when the list may not cover everyone. *Fix:* add an escape option.

**Overlapping/!mutually-exclusive categories 🟠** — pick-one lists whose items overlap. *Fix:* make them exclusive or allow multi-select.

## Structure (whole instrument)

**Order / priming 🟠** — a specific or flattering item before a general one biases the general answer (praise the brand → then ask overall satisfaction). *Fix:* general/overall questions first, specific later; randomize where possible.

**Sensitive without opt-out 🟡** — age, income, health, race, religion, gender identity, political, immigration, etc. Drives drop-off or false answers. *Fix:* make optional + "Prefer not to say"; place late.

**Length / fatigue 🟡** — very long surveys lower data quality near the end. *Fix:* cut to the decisions you'll actually make.

**Missing "screen-out" / consistency check 🟡** — no attention check on long panels. *Fix:* add one if quality matters.

## Likert quick-reference

- 5-point agreement: Strongly disagree / Disagree / Neither / Agree / Strongly agree.
- 5-point satisfaction: Very dissatisfied / Dissatisfied / Neither / Satisfied / Very satisfied.
- Keep anchors symmetric, label every point (not just the ends), and keep one scale direction consistent across the survey.
