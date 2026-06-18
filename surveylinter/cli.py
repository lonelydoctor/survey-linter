"""Command-line interface for survey-linter."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .importers import load_path, load_text, FORMATS
from .engine import lint_questions
from .config import load_config
from .lexicons import available
from .model import SEV_RANK
from . import report as _report
from . import fix as _fix


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="surveylinter",
        description="Audit a survey/questionnaire for biased questions before you send it.",
    )
    p.add_argument("inputs", nargs="*", help="survey file(s); omit or use '-' for stdin")
    p.add_argument("--text", help="lint this string directly instead of reading a file")
    p.add_argument("-f", "--format", default="auto", choices=FORMATS,
                   help="input format (default: auto-detect)")
    p.add_argument("-l", "--lang", default="auto",
                   help="language: " + ", ".join(available()) + ", or auto (default)")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    p.add_argument("--fix", action="store_true", help="print deterministic suggested revisions")
    p.add_argument("-c", "--config", help="path to .surveylinterrc (default: auto-discover)")
    p.add_argument("--fail-on", choices=["high", "med", "low", "any", "none"],
                   help="exit nonzero if an issue at/above this severity exists (CI gate)")
    p.add_argument("--min-score", type=int, help="exit nonzero if score is below N (CI gate)")
    p.add_argument("-V", "--version", action="version", version=f"survey-linter {__version__}")
    return p


def _should_fail(report, fail_on: Optional[str], min_score: Optional[int]) -> bool:
    if min_score is not None and report.score.value < min_score:
        return True
    if fail_on and fail_on != "none":
        findings = report.all_findings()
        if fail_on == "any":
            return bool(findings)
        thr = SEV_RANK[fail_on]
        return any(SEV_RANK[f.severity] >= thr for f in findings)
    return False


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(path=args.config)
    except (ValueError, OSError) as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2

    results = []  # list[(label, report)]
    try:
        if args.text is not None:
            qs = load_text(args.text, fmt=args.format)
            results.append((None, lint_questions(qs, lang=args.lang, config=config)))
        elif not args.inputs or args.inputs == ["-"]:
            qs = load_text(sys.stdin.read(), fmt=args.format)
            results.append((None, lint_questions(qs, lang=args.lang, config=config)))
        else:
            for path in args.inputs:
                qs = load_path(path, fmt=args.format)
                results.append((path, lint_questions(qs, lang=args.lang, config=config)))
    except FileNotFoundError as e:
        print(f"file not found: {e.filename}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"could not parse input: {e}", file=sys.stderr)
        return 2

    if args.json:
        if len(results) == 1:
            print(_report.render_json(results[0][1]))
        else:
            import json
            print(json.dumps([dict(file=label, **rep.to_dict()) for label, rep in results],
                             ensure_ascii=False, indent=2))
    else:
        for i, (label, rep) in enumerate(results):
            if label and len(results) > 1:
                print(f"===== {label} =====")
            print(_fix.render_fixes(rep) if args.fix else _report.render_human(rep))
            if i != len(results) - 1:
                print()

    fail_on = args.fail_on or (config.fail_on if config else None)
    min_score = args.min_score if args.min_score is not None else (config.min_score if config else None)
    return 1 if any(_should_fail(rep, fail_on, min_score) for _, rep in results) else 0


if __name__ == "__main__":
    sys.exit(main())
