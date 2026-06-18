"""`.surveylinterrc` config loading (JSON, stdlib only).

Keys (all optional):
  language : "en" | "zh"            force a language
  disable  : ["rule_code", ...]     turn rules off
  severity : {"rule_code": "low"}   override a rule's severity
  ignore   : ["regex", ...]         skip questions whose text matches
  fail_on  : "high"|"med"|"low"|"any"|"none"   CI gate
  min_score: 0..100                  CI gate
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

CONFIG_NAMES = (".surveylinterrc", ".surveylinterrc.json")


@dataclass
class Config:
    language: Optional[str] = None
    disabled: List[str] = field(default_factory=list)
    severity: Dict[str, str] = field(default_factory=dict)
    ignore: List[str] = field(default_factory=list)
    fail_on: Optional[str] = None
    min_score: Optional[int] = None
    _ignore_re: list = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self._ignore_re = []
        for pat in self.ignore:
            try:
                self._ignore_re.append(re.compile(pat, re.I))
            except re.error:
                pass

    def is_ignored(self, text: str) -> bool:
        return any(r.search(text) for r in self._ignore_re)


def find_config(start: str = ".") -> Optional[str]:
    d = os.path.abspath(start)
    while True:
        for name in CONFIG_NAMES:
            p = os.path.join(d, name)
            if os.path.isfile(p):
                return p
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def load_config(path: Optional[str] = None, start: str = ".") -> Optional[Config]:
    if path is None:
        path = find_config(start)
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    sev = data.get("severity", {}) or {}
    return Config(
        language=data.get("language"),
        disabled=list(data.get("disable", []) or data.get("disabled", []) or []),
        severity={k: str(v) for k, v in sev.items()},
        ignore=list(data.get("ignore", []) or []),
        fail_on=data.get("fail_on") or data.get("fail-on"),
        min_score=(data.get("min_score") if data.get("min_score") is not None
                   else data.get("min-score")),
    )
