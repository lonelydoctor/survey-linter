"""Format importers: Google Forms, Typeform, Qualtrics QSF, and auto-sniffing."""
import json
import unittest

from surveylinter.importers import load_text, google_forms, typeform, qualtrics

GOOGLE = {
    "items": [
        {"title": "How fast and friendly is support?",
         "questionItem": {"question": {"choiceQuestion": {"type": "RADIO",
             "options": [{"value": "Yes"}, {"value": "No"}]}}}},
        {"title": "Rate these aspects",
         "questionGroupItem": {
             "grid": {"columns": {"options": [{"value": "Good"}, {"value": "Bad"}]}},
             "questions": [{"rowQuestion": {"title": "Speed"}},
                           {"rowQuestion": {"title": "Price"}}]}},
    ]
}

TYPEFORM = {
    "fields": [
        {"title": "How satisfied are you with price and quality?", "type": "multiple_choice",
         "properties": {"choices": [{"label": "Good"}, {"label": "Bad"}]}},
        {"title": "Rate us", "type": "opinion_scale",
         "properties": {"steps": 10, "labels": {"left": "Bad", "right": "Good"}}},
    ]
}

QSF = {
    "SurveyElements": [
        {"Element": "SQ", "Payload": {"QuestionText": "How much do you love our app?",
            "QuestionType": "MC", "Selector": "SAVR",
            "Choices": {"1": {"Display": "Yes"}, "2": {"Display": "No"}}}},
        {"Element": "SQ", "Payload": {"QuestionText": "Rate aspects", "QuestionType": "Matrix",
            "Choices": {"1": {"Display": "Speed"}, "2": {"Display": "Price"}},
            "Answers": {"1": {"Display": "Good"}, "2": {"Display": "Bad"}}}},
    ]
}


class GoogleForms(unittest.TestCase):
    def test_parse(self):
        qs = google_forms.parse(GOOGLE)
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0].options, ["Yes", "No"])
        self.assertEqual(qs[1].qtype, "matrix")
        self.assertEqual(qs[1].rows, ["Speed", "Price"])

    def test_sniff(self):
        self.assertEqual(len(load_text(json.dumps(GOOGLE))), 2)


class Typeform(unittest.TestCase):
    def test_parse(self):
        qs = typeform.parse(TYPEFORM)
        self.assertEqual(qs[0].options, ["Good", "Bad"])
        self.assertEqual(qs[1].qtype, "scale")

    def test_sniff(self):
        self.assertEqual(len(load_text(json.dumps(TYPEFORM))), 2)


class Qualtrics(unittest.TestCase):
    def test_parse(self):
        qs = qualtrics.parse(QSF)
        self.assertEqual(qs[0].options, ["Yes", "No"])
        self.assertEqual(qs[1].rows, ["Speed", "Price"])
        self.assertEqual(qs[1].options, ["Good", "Bad"])

    def test_sniff(self):
        self.assertEqual(len(load_text(json.dumps(QSF))), 2)

    def test_strips_html(self):
        data = {"SurveyElements": [{"Element": "SQ", "Payload": {
            "QuestionText": "<b>Are you happy?</b>", "QuestionType": "TE"}}]}
        self.assertEqual(qualtrics.parse(data)[0].text, "Are you happy?")


class EndToEnd(unittest.TestCase):
    def test_lint_imported(self):
        # the imported Google Forms survey should still trip the double-barreled rule
        import surveylinter as sl
        rep = sl.lint_text(json.dumps(GOOGLE), lang="en")
        found = {f.code for q in rep.questions for f in q.findings}
        self.assertIn("double_barreled", found)


if __name__ == "__main__":
    unittest.main()
