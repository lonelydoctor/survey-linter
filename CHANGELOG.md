# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project uses
[semantic versioning](https://semver.org/).

## [0.2.0] — 2026-06-17

A major expansion from a single script into a small, tested, multilingual package
— while keeping it zero-dependency and keeping the original command working.

### Added
- **Multilingual rule packs** — English and Simplified Chinese (`--lang zh`, or
  auto-detected). New languages are a single file under `surveylinter/lexicons/`.
- **Transparent quality score** — a 0–100 score + letter grade whose formula is
  printed in the report and reproducible by hand (no black box).
- **`--fix`** — deterministic suggested revisions (balanced scales, exclusive
  ranges, optional sensitive items, split templates).
- **Multi-format importers** — Markdown, CSV, Google Forms (API JSON), Typeform
  (form JSON), and Qualtrics `.qsf`, plus matrix/grid, branching and piped-text
  handling. Auto-detected or forced with `--format`.
- **Configuration** via `.surveylinterrc` (disable rules, override severities,
  ignore patterns, force language, CI gates).
- **CI integrations** — a composite **GitHub Action**, a **pre-commit** hook, and
  CLI exit-code gates (`--fail-on`, `--min-score`). GitHub Actions CI on 3.9–3.13.
- **Browser demo** (`web/index.html`) running the real engine client-side via
  Pyodide — nothing is uploaded.
- **New checks** — recall burden, ambiguous referent, piped/dynamic text,
  non-exhaustive option lists, slash ambiguity.
- **Packaging** (`pyproject.toml`) exposing a `surveylinter` console command.
- **Test suite** (49 stdlib `unittest` cases).

### Changed
- Logic moved from a single script into the `surveylinter` package. The original
  `python scripts/lint_survey.py file [--json]` command still works unchanged.
- README repositioned around the real differentiators (deterministic, local,
  embeddable, multilingual) now that comparable tools exist.

## [0.1.0] — 2026-06-15

### Added
- Initial release: deterministic question-quality linter (`scripts/lint_survey.py`)
  + Claude skill (`SKILL.md`), rule catalog, report template, and a worked example.
