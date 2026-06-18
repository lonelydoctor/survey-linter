# Contributing

Thanks for helping make survey-linter better. Two design rules keep it simple:

1. **Zero runtime dependencies** — standard library only.
2. **Deterministic & verifiable** — a rule should point to exact wording the user
   can check. Judgment calls belong in the skill's judgment layer, not the engine.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

No dependencies needed. Please add a test for any rule or importer you touch.

## Add a rule

1. Write a function `(Question, Lexicon) -> list[Finding]` in `surveylinter/rules.py`
   (wording), `scales.py` (response options), or `structure.py` (whole instrument).
   Read language-specific cues from the `Lexicon` so it works in every language;
   localize the message with `_util.L(lex, en, zh)`.
2. Register it in that module's rule list (`QUESTION_RULES` / `SCALE_RULES`).
3. Give the finding a stable `code` (so users can `disable`/re-`severity` it via
   `.surveylinterrc`), document it in `references/rule_catalog.md`, and add a test.

## Add a language

1. Copy `surveylinter/lexicons/en.py` to `surveylinter/lexicons/<code>.py`, translate
   the word lists, and set `cjk` / `length_unit` / `length_max` appropriately.
2. Register it in `surveylinter/lexicons/__init__.py` and, if needed, teach
   `detect_language` how to recognize the script.
3. Add a few tests under `tests/`.

## Add an importer

Add `surveylinter/importers/<format>.py` exposing `parse(data) -> list[Question]`,
wire it into `importers/__init__.py` (dispatch + sniffing), and add a test with a
small inline sample.
