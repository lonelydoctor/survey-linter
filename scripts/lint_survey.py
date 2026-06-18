#!/usr/bin/env python3
"""Backward-compatible entry point for the deterministic survey linter.

The logic now lives in the `surveylinter` package (stdlib only, zero deps). This
shim keeps the documented command working and adds the v0.2 flags:

    python scripts/lint_survey.py questions.txt           # human report
    python scripts/lint_survey.py questions.txt --json     # machine-readable
    python scripts/lint_survey.py questions.txt --fix      # suggested revisions
    python scripts/lint_survey.py survey.qsf --lang zh     # other formats/langs
    cat questions.txt | python scripts/lint_survey.py -    # stdin

Equivalent to: `python -m surveylinter ...`
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from surveylinter.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
