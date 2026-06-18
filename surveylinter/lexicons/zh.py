"""Chinese (Simplified) rule-pack.

CJK has no word spaces, so matching is substring-based — entries are chosen to be
multi-character and distinctive to avoid false positives. Length is counted in
characters, and conjunction/negation cues use Chinese tokens.
"""
from __future__ import annotations

from . import Lexicon

LEXICON = Lexicon(
    code="zh",
    name="简体中文",
    cjk=True,
    length_unit="char",
    length_max=45,
    loaded=[
        "惊艳", "太棒", "超棒", "卓越", "糟糕", "糟透", "差劲", "完美", "极好",
        "难道你不觉得", "你难道不", "你不觉得", "你同意吗", "难道不是", "众所周知",
        "显然", "当然", "毫无疑问", "大家都知道", "最好", "最差", "最棒", "无与伦比",
        "屡获殊荣", "业界领先", "一流", "顶级", "无可挑剔",
    ],
    absolutes=["总是", "从不", "从来不", "全部", "所有", "每一个", "每个人", "任何人",
               "没有人", "任何时候", "无一例外", "永远", "绝对"],
    vague=["经常", "通常", "有时", "偶尔", "频繁", "很少", "一般", "大多", "多数",
           "一些", "若干", "大量", "不少", "时常", "常常"],
    presupposition=["你有多喜欢", "你有多爱", "你有多满意于", "为什么更好",
                    "你为什么喜欢", "你有多讨厌", "你有多享受"],
    sensitive=["年龄", "收入", "工资", "薪水", "薪资", "种族", "民族", "宗教", "信仰",
               "健康", "疾病", "病史", "残疾", "性取向", "性别认同", "政治", "党派",
               "移民", "国籍", "户籍", "体重", "怀孕", "犯罪", "被捕", "前科"],
    neutral_tokens=["中立", "一般", "中等", "不确定", "不清楚", "无所谓", "说不好",
                    "不知道", "不愿透露", "不便透露", "保密"],
    pos_anchors=["非常满意", "满意", "比较满意", "很好", "较好", "优秀", "同意",
                 "非常同意", "比较同意", "很可能", "非常可能", "总是", "经常", "愿意"],
    neg_anchors=["非常不满意", "不满意", "比较不满意", "很差", "较差", "差", "不同意",
                 "非常不同意", "比较不同意", "不太可能", "非常不可能", "从不", "很少",
                 "不愿意"],
    conjunctions=["和", "与", "及", "以及", "并且", "而且", "还有", "或者"],
    negations=["不", "没", "没有", "无法", "未", "非", "别", "勿", "无"],
    referents=["它", "他们", "她们", "它们", "这个", "那个", "这些", "那些", "其"],
    other_tokens=["其他", "其它", "以上都不是", "都不是", "不适用"],
    jargon_ok={"NPS", "CSAT", "CES", "FAQ", "CEO", "CTO", "HR", "IT", "AI",
               "ID", "URL", "API", "PDF", "UX", "UI", "KPI", "OKR", "SaaS", "App"},
    recall_patterns=[
        r"(过去|最近|上一?)\s*[\d一二三四五六七八九十两半]+?\s*(年|个月|周|星期|天|季度)"
        r".{0,12}(多少次|几次|多少|多少天|多少回)",
    ],
)
