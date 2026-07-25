#!/usr/bin/env python3
"""Regression check for prebuilt wrong-answer review assets."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image


# 생성 과정에서 도형·선택지 추출이 실패한 항목("렌더 누락", 빈 선택지)은 학생에게
# 보이면 안 된다. final.html의 dhUsable()과 같은 규칙으로 손상 개수를 감시한다.
PLACEHOLDER = re.compile(
    r"(?:렌더|렌더링|추출|복원|원본)[^\n]{0,30}?누락|누락[^\n]{0,30}?(?:렌더|렌더링|추출|복원)|렌더\s*실패|추출\s*실패|복원되지\s*않"
)


def dh_usable(analogue: dict) -> bool:
    stem = str(analogue.get("stem") or analogue.get("stemHtml") or "")
    expl = str(analogue.get("explanation") or analogue.get("explanationHtml") or "")
    if not stem.strip() and not analogue.get("image"):
        return False
    if PLACEHOLDER.search(stem + expl):
        return False
    choices = analogue.get("choices") or analogue.get("choicesHtml") or []
    if len(choices) < 4:
        return False
    return all(str(c or "").strip() for c in choices)


# 현재 알려진 손상 항목 수(2400 중). 데이터를 고치면 이 값을 낮추고,
# 늘어나면(=새 손상 유입) 테스트가 실패하도록 상한으로 고정한다.
BROKEN_BUDGET = 133

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "final.html").read_text(encoding="utf-8")
exams = json.loads(source.split("const FINAL_EXAMS=", 1)[1].split(";\n", 1)[0])

expected = sum(exam["nQ"] for exam in exams)
seen = 0
broken = 0

for exam in exams:
    answers = json.loads(
        (ROOT / "answers" / f"{exam['id']}.json").read_text(encoding="utf-8")
    )["questions"]
    analogues = json.loads(
        (ROOT / "donghyung" / f"{exam['id']}.json").read_text(encoding="utf-8")
    )["questions"]
    assert len(answers) == exam["nQ"], exam["id"]
    assert len(analogues) == exam["nQ"], exam["id"]
    for number in range(1, exam["nQ"] + 1):
        key = str(number)
        crop = ROOT / "crops" / exam["id"] / f"{number}.png"
        with Image.open(crop) as image:
            image.verify()
        analogue = analogues[key]
        assert analogue["answer"] in (1, 2, 3, 4), (exam["id"], number)
        assert analogue["verified"] is True, (exam["id"], number)
        # 구 DB는 기출 이미지를 끌어와 explanationHtml 을 가지고, 재집필본(origin=authored)은
        # 글자만으로 완결되므로 explanation/이미지 요구가 다르다.
        authored = analogue.get("origin") == "authored"
        if authored:
            assert analogue["explanation"], (exam["id"], number)
            assert len(analogue.get("choices") or []) == 4, (exam["id"], number)
            for banned in ("sourceExamId", "sourceQuestion", "matchLevel"):
                assert not analogue.get(banned), (exam["id"], number, banned)
        else:
            assert analogue["explanationHtml"], (exam["id"], number)
            assert (ROOT / analogue["image"]).exists(), (exam["id"], number)
        expected_misconceptions = {
            str(option)
            for option in range(1, 5)
            if option != analogue["answer"]
        }
        assert expected_misconceptions.issubset(
            analogue["misconceptions"]
        ), (exam["id"], number)
        assert answers[key]["answer"] == exam["key"][number - 1], (
            exam["id"],
            number,
        )
        if not dh_usable(analogue):
            broken += 1
        seen += 1

# 오답정리는 '다시 풀고 제출'하는 채점형이 아니라, 동형문제·정답·해설을 바로 보여주는
# 간단 학습 카드로 개선됨(wbCardHTML). 채점 함수(wbGradeOriginal/wbGradeAnalogue)는 설계상 제거.
for function in (
    "wrongbookShell",
    "wbCardHTML",
    "hydrateWrongbook",
    "downloadReportPDF",
    "dhUsable",
):
    assert re.search(rf"function\s+{function}\s*\(", source), function

# 손상 항목은 dhUsable() 가드로 숨겨지지만, 새로 늘어나면 즉시 잡는다.
assert broken <= BROKEN_BUDGET, f"손상 동형문제 증가: {broken} > {BROKEN_BUDGET}"

assert seen == expected == 2400
print(
    f"PASS wrongbook assets: exams={len(exams)} questions={seen} "
    f"손상(가드로 숨김)={broken}/{BROKEN_BUDGET}"
)
