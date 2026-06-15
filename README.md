<h1 align="center">survey-linter</h1>

<p align="center">
  <b>A Claude skill that catches the biased questions in your survey — before you send it.</b><br/>
  Leading, double-barreled, loaded, and double-negative wording · unbalanced or overlapping scales · missing neutral options · sensitive questions without an opt-out · question-order priming.
</p>

<p align="center">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green" />
  <img alt="type" src="https://img.shields.io/badge/Claude-Agent%20Skill-6aa6ff" />
  <img alt="deps" src="https://img.shields.io/badge/runtime-no%20deps-success" />
</p>

---

## Why

Most surveys are written by people who know their topic but not **measurement**. So the data comes back quietly biased — a leading question here, an unbalanced scale there — and you only notice after you've shipped it to 5,000 people. Survey *builders* (Typeform, SurveyMonkey, Google Forms) help you **create** questions fast; almost nothing **audits the question quality** before launch.

`survey-linter` is that missing review step. Paste your survey; get an item-by-item report of what will bias your results and a fixed version of each question.

## What it catches

- **Wording:** leading / loaded, double-barreled, presupposition, absolutes (always/never), vague quantifiers (often/regularly), double negatives, jargon, over-long items.
- **Scales:** unbalanced anchors, overlapping numeric ranges, missing neutral midpoint, too many points.
- **Structure:** question-order priming, sensitive questions without "Prefer not to say".

## Why you can trust it

The high-confidence problems are found by a **deterministic script** (`scripts/lint_survey.py`) — every flag points to exact wording you can verify. The judgment calls (is this *leading*?) are **explained, not asserted**. It never asks you to trust a black-box verdict.

## Quick start

As a Claude skill (Claude Code / Claude Desktop):

```
/plugin add ./survey-linter        # or install from a marketplace once published
```
Then just paste or point at your survey: *"review this survey before I send it."*

Or run the deterministic checks directly:

```bash
python scripts/lint_survey.py examples/sample_survey.txt
python scripts/lint_survey.py my_survey.txt --json
```

See a full before/after in [`examples/example_audit.md`](examples/example_audit.md).

## How it works

```
your survey ──▶ extract questions ──▶ lint_survey.py (deterministic flags)
                                  └──▶ judgment layer (leading/priming/recall, explained)
                                  └──▶ rewrite each flagged item ──▶ report + scorecard
```

Full taxonomy of issues and fixes: [`references/rule_catalog.md`](references/rule_catalog.md).

## Contributing

New checks are easy — add a rule to `scripts/lint_survey.py` and an entry to the rule catalog. PRs welcome.

## License

MIT
