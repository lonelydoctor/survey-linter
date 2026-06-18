"""survey-linter — audit a survey for biased questions before you send it.

Deterministic, explainable, multilingual, zero-dependency (stdlib only).

Quick use:
    import surveylinter
    report = surveylinter.lint_text("Don't you agree our amazing app is great?")
    print(report.score.value, report.score.verdict)
"""
from __future__ import annotations

__version__ = "0.2.0"

from .model import Report, Question, Finding, Score          # noqa: E402
from .engine import lint_questions                           # noqa: E402
from .lexicons import get_lexicon, available, detect_language  # noqa: E402


def lint_text(text: str, lang: str = "auto", fmt: str = "auto", config=None) -> Report:
    from .importers import load_text
    return lint_questions(load_text(text, fmt=fmt), lang=lang, config=config)


def lint_file(path: str, lang: str = "auto", fmt: str = "auto", config=None) -> Report:
    from .importers import load_path
    return lint_questions(load_path(path, fmt=fmt), lang=lang, config=config)


__all__ = [
    "__version__", "lint_text", "lint_file", "lint_questions",
    "Report", "Question", "Finding", "Score",
    "get_lexicon", "available", "detect_language",
]
