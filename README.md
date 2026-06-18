<h1 align="center">survey-linter</h1>

<p align="center">
  <b>Audit your survey for biased questions — before you send it.</b><br/>
  Deterministic · explainable · multilingual (English / 中文) · zero runtime dependencies.
</p>

<p align="center">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green" />
  <img alt="type" src="https://img.shields.io/badge/Claude-Agent%20Skill-6aa6ff" />
  <img alt="deps" src="https://img.shields.io/badge/runtime-no%20deps-success" />
  <img alt="python" src="https://img.shields.io/badge/python-3.9%2B-blue" />
  <img alt="ci" src="https://img.shields.io/badge/tests-unittest-informational" />
</p>

<p align="center">
  <a href="https://lonelydoctor.github.io/survey-linter/web/"><b>▶ Try the live demo</b></a> — runs entirely in your browser; nothing is uploaded.
</p>

---

## Why

Survey *builders* (Typeform, SurveyMonkey, Google Forms) help you **create** questions fast. Question-quality review does exist — but it's either a **black-box AI score** in a web app you paste into, or it's **locked inside one platform** (Qualtrics ExpertReview, SurveyMonkey Genius). If you write surveys outside those tools, in more than one language, or want results you can *verify*, there's a gap.

`survey-linter` fills it differently:

- **Deterministic & verifiable** — the high-confidence problems come from a rule engine, and every flag points to the exact wording. The quality **score is a formula you can reproduce by hand**, not a model you have to trust.
- **Local & private** — runs on your machine, in CI, or 100% in your browser. Your survey never has to leave your laptop.
- **Embeddable** — a CLI, a Claude skill, a GitHub Action, and a pre-commit hook. Lint surveys where you already work.
- **Multilingual** — English and Simplified Chinese today; adding a language is one file.
- **Free & open**, with **zero runtime dependencies** (standard library only).

## How it compares

| | survey-linter | Standalone AI checkers | Platform built-ins (Qualtrics / SurveyMonkey) |
|---|---|---|---|
| Verifiable (line-level, not a black box) | ✅ | ❌ (opaque) | ❌ (opaque score) |
| Runs locally / offline / in CI | ✅ | ❌ | ❌ |
| Works outside any one platform | ✅ | ✅ | ❌ |
| Multilingual rule packs | ✅ EN/中文 | partial | partial |
| Free & open source | ✅ | varies | ❌ |

## What it catches

- **Wording** — leading/loaded, double-barreled, presupposition, absolutes (always/never), vague quantifiers, double negatives, recall burden, ambiguous referents, piped/dynamic text, jargon, over-long items.
- **Scales** — unbalanced anchors, overlapping numeric ranges, missing neutral midpoint, too many points, non-exhaustive option lists.
- **Structure** — question-order priming, sensitive questions placed too early / without an opt-out, survey fatigue.

Full taxonomy with severities and fixes: [`references/rule_catalog.md`](references/rule_catalog.md).

## Quick start

**As a Claude skill** (Claude Code / Desktop): add the folder as a skill/plugin, then *"review this survey before I send it."*

**As a CLI** (zero install — stdlib only):

```bash
python scripts/lint_survey.py examples/sample_survey.txt        # human report + score
python scripts/lint_survey.py examples/sample_survey_zh.txt --lang zh
python scripts/lint_survey.py my_survey.txt --json              # machine-readable
python scripts/lint_survey.py my_survey.txt --fix              # suggested revisions
```

**Installed** (adds the `surveylinter` command, still zero runtime deps):

```bash
pip install -e .
surveylinter my_survey.md --format markdown
echo "Don't you agree our amazing app is great?" | surveylinter -
```

**Python API:**

```python
import surveylinter
report = surveylinter.lint_text("Don't you agree our amazing app is fast and friendly?")
print(report.score.value, report.score.verdict)
```

**In the browser** — open [`web/index.html`](web/index.html) (served over http, or via GitHub Pages). It runs the real engine client-side with Pyodide; nothing is uploaded.

## Input formats

Auto-detected by extension/content, or forced with `--format`:

`plaintext` · `markdown` (sections + scales) · `csv` · `google-forms` (API JSON) · `typeform` (form JSON) · `qualtrics` (`.qsf`). Matrix/grid questions, branching, and piped text are handled.

## Transparent scoring

```
Score = 100 − (🔴 high × 12 + 🟠 med × 6 + 🟡 low × 2)   # floored at 0
```

The report prints the exact arithmetic so anyone can reproduce it — no hidden model.

## Configuration — `.surveylinterrc`

Drop a JSON file in your project (auto-discovered) to tune the linter — disable rules, override severities, ignore lines, force a language, set CI gates. See [`examples/surveylinterrc.example.json`](examples/surveylinterrc.example.json).

## CI / pre-commit / GitHub Action

**GitHub Action** — fail a PR when a survey regresses:

```yaml
- uses: lonelydoctor/survey-linter@v0.2.0
  with:
    paths: surveys/*.md
    lang: auto
    fail-on: high
```

**pre-commit** — lint surveys before they're committed:

```yaml
repos:
  - repo: https://github.com/lonelydoctor/survey-linter
    rev: v0.2.0
    hooks:
      - id: survey-lint
```

Both use the CLI's exit codes (`--fail-on`, `--min-score`).

## How it works

```
survey (txt/md/csv/Forms/Typeform/QSF)
        │  importers → Question[]
        ▼
  deterministic rules ──▶ findings (each points to exact wording)
        │  + transparent score
        ▼
  report (human / JSON / suggested fixes)         ← the verifiable layer
        +
  judgment layer (subtle leading / priming / recall, explained)  ← added by the Claude skill
```

## Contributing

Adding a **rule** or a **language** is intentionally small — see [`CONTRIBUTING.md`](CONTRIBUTING.md). Run the tests with `python -m unittest discover -s tests`.

## License

MIT
