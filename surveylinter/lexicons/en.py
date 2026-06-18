"""English rule-pack. Curated to fire on real bias cues with few false positives."""
from __future__ import annotations

from . import Lexicon

LEXICON = Lexicon(
    code="en",
    name="English",
    cjk=False,
    length_unit="word",
    length_max=25,
    loaded=[
        "amazing", "awesome", "excellent", "terrible", "awful", "horrible",
        "wonderful", "fantastic", "obviously", "simply", "surely", "clearly",
        "of course", "everyone knows", "fail to", "don't you agree", "do you agree",
        "wouldn't you say", "isn't it true", "best", "worst", "greatest",
        "incredible", "outstanding", "useless", "award-winning", "world-class",
    ],
    absolutes=["always", "never", "all", "none", "every", "everyone", "everybody",
               "nobody", "no one", "any time", "each and every"],
    vague=["often", "regularly", "sometimes", "occasionally", "frequently", "rarely",
           "usually", "many", "few", "several", "a lot", "some", "most"],
    presupposition=["how much do you love", "how much do you enjoy", "why is",
                    "why do you like", "what do you love", "how great", "how much do you hate"],
    sensitive=["age", "income", "salary", "earn", "race", "ethnic", "religion",
               "religious", "health", "medical", "disability", "sexual",
               "gender identity", "political", "immigration", "citizenship",
               "weight", "pregnan", "criminal", "arrest"],
    neutral_tokens=["neutral", "neither", "no opinion", "not sure", "prefer not",
                    "n/a", "na", "don't know", "dont know", "unsure"],
    pos_anchors=["excellent", "very good", "good", "satisfied", "very satisfied",
                 "extremely satisfied", "agree", "strongly agree", "likely",
                 "very likely", "always", "often", "great", "somewhat satisfied",
                 "somewhat agree"],
    neg_anchors=["poor", "very poor", "bad", "very bad", "dissatisfied",
                 "very dissatisfied", "extremely dissatisfied", "disagree",
                 "strongly disagree", "unlikely", "very unlikely", "never", "rarely",
                 "terrible", "somewhat dissatisfied", "somewhat disagree"],
    conjunctions=["and", "as well as"],
    negations=["no", "not", "never", "none", "n't", "cannot", "can't", "without"],
    referents=["it", "they", "them", "this", "that", "these", "those"],
    other_tokens=["other", "none of these", "none of the above", "not applicable", "n/a"],
    jargon_ok={"NPS", "CSAT", "CES", "FAQ", "CEO", "CTO", "HR", "IT", "AI", "USA",
               "UK", "ID", "URL", "API", "OK", "TV", "PDF", "UX", "UI", "SaaS"},
    recall_patterns=[
        r"(how many|how often|how frequently).{0,40}\b(last|past|previous)\b.{0,15}"
        r"\b(\d+\s*)?(year|month|week|day|quarter)s?\b",
    ],
)
