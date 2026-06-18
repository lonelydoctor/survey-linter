"""Rules, scales, structure, scoring, parsing, config and fixes."""
import unittest

from surveylinter.engine import lint_questions
from surveylinter.model import Question, HIGH, MED, LOW
from surveylinter.config import Config
from surveylinter.lexicons import detect_language
from surveylinter import parse, fix


def codes(report):
    out = {f.code for q in report.questions for f in q.findings}
    out |= {f.code for f in report.structure}
    return out


def lint_one(text, lang="en", options=None, qtype=None):
    q = Question(n=1, text=text, options=options or [], qtype=qtype)
    return lint_questions([q], lang=lang)


class EnglishWording(unittest.TestCase):
    def test_double_barreled(self):
        self.assertIn("double_barreled", codes(lint_one("How fast and friendly is our support?")))

    def test_double_barreled_whitelist(self):
        self.assertNotIn("double_barreled", codes(lint_one("Do you accept the terms and conditions?")))

    def test_leading_loaded(self):
        self.assertIn("leading_loaded", codes(lint_one("Don't you agree our amazing app is great?")))

    def test_presupposition(self):
        self.assertIn("presupposition", codes(lint_one("How much do you love the new dashboard?")))

    def test_absolute(self):
        self.assertIn("absolutes", codes(lint_one("Do you always read our emails?")))

    def test_vague(self):
        self.assertIn("vague_quantifier", codes(lint_one("Do you use the product often?")))

    def test_double_negative(self):
        self.assertIn("double_negative", codes(lint_one("Would you not be unwilling to recommend us?")))

    def test_recall_burden(self):
        self.assertIn("recall_burden", codes(lint_one("How many times in the past 12 months did you call support?")))

    def test_sensitive(self):
        self.assertIn("sensitive_topic", codes(lint_one("What is your annual income?")))

    def test_jargon(self):
        self.assertIn("jargon", codes(lint_one("How satisfied are you with the ABC and the XYZ?")))

    def test_clean_passes(self):
        r = lint_one("How easy or difficult is the app to use?")
        self.assertEqual([f for q in r.questions for f in q.findings], [])


class Scales(unittest.TestCase):
    def test_overlapping(self):
        self.assertIn("overlapping_ranges", codes(lint_one("Rate us", options=["0-5", "5-10"])))

    def test_unbalanced(self):
        opts = ["Excellent", "Very good", "Good", "Satisfied", "Poor"]
        self.assertIn("unbalanced_scale", codes(lint_one("Rate support", options=opts)))

    def test_missing_neutral(self):
        opts = ["Strongly agree", "Agree", "Disagree", "Strongly disagree"]
        self.assertIn("missing_neutral", codes(lint_one("It is useful", options=opts)))

    def test_too_many_points(self):
        opts = ["Strongly agree", "Agree", "Somewhat agree", "Neutral",
                "Somewhat disagree", "Disagree", "Strongly disagree", "No opinion"]
        self.assertIn("too_many_points", codes(lint_one("Rate this", options=opts)))

    def test_non_exhaustive(self):
        self.assertIn("non_exhaustive", codes(lint_one("Pick a color", options=["Red", "Blue", "Green"], qtype="single")))


class Structure(unittest.TestCase):
    def test_priming(self):
        qs = [Question(1, "How amazing was our award-winning service?"),
              Question(2, "Overall, how satisfied are you?")]
        self.assertIn("order_priming", codes(lint_questions(qs, lang="en")))


class Scoring(unittest.TestCase):
    def test_clean_is_100(self):
        r = lint_one("How easy or difficult is the app to use?")
        self.assertEqual(r.score.value, 100)
        self.assertEqual(r.score.verdict, "ship-ready")

    def test_penalty_math(self):
        r = lint_one("Don't you agree our amazing app is great?")  # one high
        self.assertEqual(r.score.value, 100 - 12)


class Chinese(unittest.TestCase):
    def test_detect(self):
        self.assertEqual(detect_language("请问您的年收入是多少？"), "zh")

    def test_loaded(self):
        self.assertIn("leading_loaded", codes(lint_one("难道你不觉得我们这个超棒的产品很好吗？", lang="zh")))

    def test_absolute(self):
        self.assertIn("absolutes", codes(lint_one("您是否总是使用我们的产品？", lang="zh")))

    def test_sensitive(self):
        self.assertIn("sensitive_topic", codes(lint_one("请问您的收入是多少？", lang="zh")))

    def test_double_barreled(self):
        self.assertIn("double_barreled", codes(lint_one("您对我们的价格和质量是否满意呢？", lang="zh")))


class Parsing(unittest.TestCase):
    def test_scale_attaches(self):
        qs = parse.parse_plaintext("1. How good is it?\nExcellent, Good, Fair, Poor")
        self.assertEqual(len(qs), 1)
        self.assertEqual(len(qs[0].options), 4)

    def test_inline_options(self):
        qs = parse.parse_plaintext("Rate our service: 0-5, 5-10")
        self.assertEqual(qs[0].options, ["0-5", "5-10"])

    def test_markdown_sections(self):
        qs = parse.parse_markdown("## Demographics\n- What is your age?")
        self.assertEqual(qs[0].section, "Demographics")

    def test_csv(self):
        qs = parse.parse_csv("question,options\nHow are you?,Good;Bad\n")
        self.assertEqual(qs[0].text, "How are you?")
        self.assertEqual(qs[0].options, ["Good", "Bad"])


class ConfigBehavior(unittest.TestCase):
    def test_disable(self):
        cfg = Config(disabled=["leading_loaded"])
        self.assertNotIn("leading_loaded", codes(lint_questions(
            [Question(1, "Don't you agree it's amazing?")], lang="en", config=cfg)))

    def test_severity_override(self):
        cfg = Config(severity={"sensitive_topic": "high"})
        r = lint_questions([Question(1, "What is your income?")], lang="en", config=cfg)
        sev = [f.severity for q in r.questions for f in q.findings if f.code == "sensitive_topic"]
        self.assertEqual(sev, [HIGH])

    def test_ignore(self):
        cfg = Config(ignore=["income"])
        r = lint_questions([Question(1, "What is your income?")], lang="en", config=cfg)
        self.assertEqual([f for q in r.questions for f in q.findings], [])

    def test_force_language(self):
        cfg = Config(language="zh")
        r = lint_questions([Question(1, "您是否总是使用？")], config=cfg)
        self.assertEqual(r.lang, "zh")


class Fixes(unittest.TestCase):
    def test_balanced_suggestion(self):
        r = lint_one("Rate support", options=["Excellent", "Very good", "Good", "Satisfied", "Poor"])
        self.assertIn("balanced", fix.render_fixes(r).lower())

    def test_exclusive_ranges(self):
        r = lint_one("Rate us", options=["0-5", "5-10"])
        self.assertIn("exclusive", fix.render_fixes(r).lower())


if __name__ == "__main__":
    unittest.main()
