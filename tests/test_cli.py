"""CLI behavior: output modes and CI exit codes."""
import contextlib
import io
import json
import unittest

from surveylinter.cli import main


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue()


class CLI(unittest.TestCase):
    def test_human_report(self):
        rc, out = run(["--text", "Don't you agree it's amazing?", "--lang", "en"])
        self.assertEqual(rc, 0)
        self.assertIn("SURVEY LINT REPORT", out)

    def test_json_output(self):
        rc, out = run(["--text", "What is your income?", "--json", "--lang", "en"])
        self.assertEqual(rc, 0)
        self.assertIn("score", json.loads(out))

    def test_fix_output(self):
        rc, out = run(["--text", "How fast and friendly is support?", "--fix", "--lang", "en"])
        self.assertIn("Split", out)

    def test_fail_on_high_trips(self):
        rc, _ = run(["--text", "Don't you agree it's amazing?", "--fail-on", "high", "--lang", "en"])
        self.assertEqual(rc, 1)

    def test_fail_on_high_clean(self):
        rc, _ = run(["--text", "How easy or difficult is the app to use?", "--fail-on", "high", "--lang", "en"])
        self.assertEqual(rc, 0)

    def test_min_score_trips(self):
        rc, _ = run(["--text", "Don't you agree our amazing app is great?", "--min-score", "95", "--lang", "en"])
        self.assertEqual(rc, 1)

    def test_lang_zh(self):
        rc, out = run(["--text", "请问您的收入是多少？", "--lang", "zh"])
        self.assertIn("收入", out)


if __name__ == "__main__":
    unittest.main()
