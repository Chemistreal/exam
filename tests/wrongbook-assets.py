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
BROKEN_BUDGET = 0

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "final.html").read_text(encoding="utf-8")
exams = json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))

# 한 시험에 동형문제 세트가 여러 벌 있을 수 있다. final.html 의 DH_SETS 를 그대로 읽어
# 모든 세트를 검사한다(여기서 놓치면 두 번째 세트가 검증 없이 학생에게 나간다).
DH_SETS = json.loads(
    re.sub(r"'", '"', source.split("const DH_SETS=", 1)[1].split("};", 1)[0] + "}")
)


def analogue_sets(exam_id: str) -> list[str]:
    return DH_SETS.get(exam_id, [exam_id])


expected = sum(len(analogue_sets(exam["id"])) * exam["nQ"] for exam in exams)
seen = 0
broken = 0

for exam in exams:
    answers = json.loads(
        (ROOT / "answers" / f"{exam['id']}.json").read_text(encoding="utf-8")
    )["questions"]
    assert len(answers) == exam["nQ"], exam["id"]
    sets = []
    for set_id in analogue_sets(exam["id"]):
        qs = json.loads(
            (ROOT / "donghyung" / f"{set_id}.json").read_text(encoding="utf-8")
        )["questions"]
        assert len(qs) == exam["nQ"], (exam["id"], set_id)
        sets.append((set_id, qs))
    for number in range(1, exam["nQ"] + 1):
        key = str(number)
        crop = ROOT / "crops" / exam["id"] / f"{number}.png"
        with Image.open(crop) as image:
            image.verify()
        assert answers[key]["answer"] == exam["key"][number - 1], (exam["id"], number)
        for set_id, analogues in sets:
            analogue = analogues[key]
            assert analogue["answer"] in (1, 2, 3, 4), (set_id, number)
            assert analogue["verified"] is True, (set_id, number)
            # 구 DB는 기출 이미지를 끌어와 explanationHtml 을 가지고, 재집필본(origin=authored)은
            # 글자만으로 완결되므로 explanation/이미지 요구가 다르다.
            authored = analogue.get("origin") == "authored"
            if authored:
                assert analogue["explanation"], (set_id, number)
                assert len(analogue.get("choices") or []) == 4, (set_id, number)
                for banned in ("sourceExamId", "sourceQuestion", "matchLevel"):
                    assert not analogue.get(banned), (set_id, number, banned)
            else:
                assert analogue["explanationHtml"], (set_id, number)
                assert (ROOT / analogue["image"]).exists(), (set_id, number)
            expected_misconceptions = {
                str(option)
                for option in range(1, 5)
                if option != analogue["answer"]
            }
            assert expected_misconceptions.issubset(
                analogue["misconceptions"]
            ), (set_id, number)
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

# seen == expected 는 "모든 문항이 자산을 갖췄나" 를 본다. 뒤의 총합은 그와
# 별개로 **조용히 사라지지 않았나** 를 본다 — 회차 하나가 통째로 빠져도 앞
# 조건은 여전히 맞기 때문이다.
#
# ⚠ 이 수는 함부로 내리지 않는다. 내려도 되는 때는 회차를 **일부러** 뺐을
#    때뿐이고, 그때는 왜 뺐는지 여기 적는다.
#    2400 → 2250 : KMChC 일반과정 세 회차(2025-1·2025-2·2026-1, 50문항씩)를
#    뺐다. 같은 회차의 심화과정만 보기로 해서다 (2026-08-08).
#    2250 → 2310 : KMChC 2012 회차를 새로 넣었다(60문항). 원본 문제지 PDF 가
#    있어야 크롭을 뜰 수 있는데 2012 년까지가 그 경계다 (2026-08-08).
#    2310 → 2370 : KMChC 2011 회차를 새로 넣었다(60문항) (2026-08-08).
#    2370 → 2430 : KMChC 2010 회차를 새로 넣었다(60문항) (2026-08-08).
#    2430 → 2490 : KMChC 2009 회차를 새로 넣었다(60문항). 문제지 PDF 가 있는
#    가장 오래된 회차다 — 2003~2008 은 문제지가 없어 크롭을 뜰 수 없다 (2026-08-08).
assert seen == expected, f"자산이 빠진 문항이 있다: {seen} != {expected}"
#    2490 → 2540 : KMChC 2025 제1차 **일반**(50문항)을 되살렸다. 맨 위 2400 → 2250
#    에서 뺐던 셋 중 하나다 — 선생님이 그 회차 교재를 새로 만들어 다시 보기로
#    하셨다. 나머지 둘(2025-2·2026-1 일반)은 그대로 빠져 있다 (2026-08-18).
assert seen == 2540, f"문항 총합이 달라졌다: {seen} (기대 2540)"
print(
    f"PASS wrongbook assets: exams={len(exams)} questions={seen} "
    f"손상(가드로 숨김)={broken}/{BROKEN_BUDGET}"
)
