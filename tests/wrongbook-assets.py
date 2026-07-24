#!/usr/bin/env python3
"""Regression check for prebuilt wrong-answer review assets."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "final.html").read_text(encoding="utf-8")
exams = json.loads(source.split("const FINAL_EXAMS=", 1)[1].split(";\n", 1)[0])

expected = sum(exam["nQ"] for exam in exams)
seen = 0

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
        assert analogue["explanationHtml"], (exam["id"], number)
        expected_misconceptions = {
            str(option)
            for option in range(1, 5)
            if option != analogue["answer"]
        }
        assert expected_misconceptions.issubset(
            analogue["misconceptions"]
        ), (exam["id"], number)
        assert (ROOT / analogue["image"]).exists(), (exam["id"], number)
        assert answers[key]["answer"] == exam["key"][number - 1], (
            exam["id"],
            number,
        )
        seen += 1

for function in (
    "wrongbookShell",
    "hydrateWrongbook",
    "wbGradeOriginal",
    "wbGradeAnalogue",
    "downloadReportPDF",
):
    assert re.search(rf"function\s+{function}\s*\(", source), function

assert seen == expected == 2400
print(f"PASS wrongbook assets: exams={len(exams)} questions={seen}")
