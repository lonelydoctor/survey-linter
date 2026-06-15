# Report template + good/bad pairs

## Report skeleton

```
SURVEY LINT REPORT
Verdict: <ship-ready | minor fixes | needs work> — N questions, M issues (X high)

— Per question —
Q<n>. "<verbatim question>"
  <🔴/🟠/🟡> <Issue name> — <why it biases responses, naming the exact words>
  ✅ Rewrite: <corrected version(s); split if double-barreled>

— Structural —
  <🔴/🟠/🟡> Scale on Q<n>: <problem> → <fix>
  <🟡> Order: <priming risk> → <fix>
  <🟡> Sensitive: Q<n> <topic> → make optional + "Prefer not to say"

— Note —
Deterministic flags (from lint_survey.py) are verifiable line-by-line; judgment calls are explained so you decide.
```

## Before → after pairs (use as exemplars in rewrites)

| Problem | Before | After |
|---|---|---|
| Double-barreled | "How satisfied are you with our fast, friendly support?" | Two items: "…with the **speed** of support?" / "…with the **friendliness** of support?" |
| Leading | "How much did you enjoy our award-winning app?" | "How would you rate your experience with the app?" |
| Presupposition | "Why do you prefer us over competitors?" | "Do you prefer us, a competitor, or have no preference?" → then "Why?" |
| Absolute | "Do you always read our emails?" | "In a typical month, how many of our emails do you open?" (ranges) |
| Vague | "Do you use the app often?" | "How many days in the past week did you use the app?" |
| Double negative | "Would you not be unwilling to renew?" | "How likely are you to renew?" |
| Unbalanced scale | Excellent / Very good / Good / Fair / Poor | Very satisfied / Satisfied / Neutral / Dissatisfied / Very dissatisfied |
| Overlapping ranges | 0–5, 5–10, 10–15 | 0–4, 5–9, 10–14, 15+ |
| Sensitive | "What is your income?" (required) | "What is your income? *(optional)*" + "Prefer not to say" |
