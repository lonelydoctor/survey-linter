"""Load surveys from many formats into a common list of Question objects.

Auto-detection: by file extension when a path is known, else by sniffing JSON
shape. Plain text / markdown / CSV are parsed by ``surveylinter.parse``; the
platform exports (Google Forms, Typeform, Qualtrics QSF) have dedicated parsers.
"""
from __future__ import annotations

import json
import os
from typing import List

from ..model import Question
from .. import parse as _parse
from . import google_forms, typeform, qualtrics

FORMATS = ("auto", "plaintext", "markdown", "csv", "google-forms", "typeform", "qualtrics")


def _sniff_json(data) -> str:
    if isinstance(data, dict):
        if "SurveyElements" in data or "SurveyEntry" in data:
            return "qualtrics"
        if isinstance(data.get("fields"), list):
            return "typeform"
        if isinstance(data.get("items"), list):
            return "google-forms"
    return ""


def _parse_json(data, kind: str) -> List[Question]:
    if kind == "qualtrics":
        return qualtrics.parse(data)
    if kind == "typeform":
        return typeform.parse(data)
    return google_forms.parse(data)


def load_text(text: str, fmt: str = "auto", filename: str = "") -> List[Question]:
    fmt = (fmt or "auto").lower()
    if fmt == "auto":
        ext = os.path.splitext(filename)[1].lower() if filename else ""
        stripped = text.lstrip()
        if ext == ".qsf":
            fmt = "qualtrics"
        elif ext == ".csv":
            fmt = "csv"
        elif ext in (".md", ".markdown"):
            fmt = "markdown"
        elif ext == ".json" or (stripped[:1] in "{["):
            try:
                data = json.loads(text)
                kind = _sniff_json(data)
                if kind:
                    return _parse_json(data, kind)
            except ValueError:
                pass
            fmt = "plaintext"
        else:
            fmt = "plaintext"
    if fmt in ("google-forms", "typeform", "qualtrics"):
        return _parse_json(json.loads(text), fmt)
    if fmt == "csv":
        return _parse.parse_csv(text)
    if fmt == "markdown":
        return _parse.parse_markdown(text)
    return _parse.parse_plaintext(text)


def load_path(path: str, fmt: str = "auto") -> List[Question]:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    return load_text(text, fmt=fmt, filename=path)
