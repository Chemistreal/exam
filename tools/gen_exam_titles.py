#!/usr/bin/env python3
"""`AppsScript-Code.gs` 의 EXAM_TITLES 를 `exams.json` + 옛 시험 목록에서 만든다.

시트는 시험을 **제목 문자열**로 구분한다. 저장(doPost)은 `d.exam = cur.title` 로
제목을 쓰고, 불러오기(doGet)는 시험 id 를 받아 제목으로 바꿔 그 행만 거른다.
그 사이를 잇는 것이 EXAM_TITLES 다.

여기에 시험이 빠져 있으면 `want` 가 null 이 되어 **모든 시험의 행을 그대로
돌려준다.** 다른 시험 응시 기록이 통계 풀에 섞여 들어간다는 뜻이다. 실제로
이 표에는 옛 kch* 시험 9개만 있었고 지금 쓰는 38개는 하나도 없었다.

제목은 바뀐다. 화올을 KMChC 로 합칠 때 '화올 2018' → 'KMChC 2018' 로 바꿨는데,
시트에 이미 쌓인 행은 옛 제목 그대로다. 그래서 id 하나에 제목을 **여러 개**
달 수 있게 하고, 지나간 제목을 HISTORY 에 적어 둔다. 옛 기록을 잃지 않으려면
제목을 바꿀 때마다 여기에 한 줄 추가해야 한다.

사용:
    python3 tools/gen_exam_titles.py            # 만들어질 블록을 보여만 준다
    python3 tools/gen_exam_titles.py --write    # AppsScript-Code.gs 에 써 넣는다
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GS = ROOT / "AppsScript-Code.gs"

BEGIN = "var EXAM_TITLES = {"
END = "};"

# 지나간 제목. 시트에 이 이름으로 쌓인 행이 있으므로 계속 인정한다.
# 제목을 바꾸면 옛 이름을 여기에 남긴다.
HISTORY = {
    # '화올'은 KMChC 의 옛 이름이었다. 전 연도를 KMChC 로 바꿨으므로 옛 이름을 남긴다.
    "hwol-2013": ["화올 2013"],
    "hwol-2014": ["화올 2014"],
    "hwol-2015": ["화올 2015"],
    "hwol-2016": ["화올 2016"],
    "hwol-2017": ["화올 2017"],
    "hwol-2021": ["화올 2021"],
    "hwol-2022": ["화올 2022"],
    "hwol-2023": ["화올 2023"],
    # 이 셋은 KMChC 쪽과 합치면서 '· 동형 2세트'를 붙였다가 다시 뗐다.
    "hwol-2018": ["화올 2018", "KMChC 2018 · 동형 2세트"],
    "hwol-2019": ["화올 2019", "KMChC 2019 · 동형 2세트"],
    "hwol-2024": ["화올 2024", "KMChC 2024 제1차 · 동형 2세트"],
}

# 없앤 id → 남긴 id. final.html 의 COHORT_ALIAS 와 같아야 한다.
MERGED = {"kmchc-2018": "hwol-2018", "kmchc-2019": "hwol-2019", "kmchc-2024-1": "hwol-2024"}

# `index.html` 의 옛 시험들. **exams.json 에는 없지만 지우면 안 된다.**
# index.html 은 final.html 과 **같은 시트 엔드포인트**를 쓰고, 같은 doGet 으로
# 명단을 받아 간다. 이 표에서 빠지면 필터가 통째로 꺼져서(want=null) 그 요청에
# **모든 시험의 행**이 딸려 간다 — 옛 시험 통계에 KMChC 응시 기록이 섞인다.
# 한 번 지웠다가 되살렸다. exams.json 만 보고 표를 다시 만들면 안 된다.
LEGACY = {
    "kch1to3":   "화학1 1-3단원 모의고사",
    "kch1to2":   "화학1 1-2단원 모의고사",
    "kch1u1":    "화학1 1단원 모의고사",
    "kch2final": "화학2 총괄평가",
    "chem2-1":   "화학2 1단원 모의고사",
    "kch1to3-b": "화학1 1-3단원 모의고사 (동형)",
    "kch1to2-b": "화학1 1-2단원 모의고사 (동형)",
    "kch2to3":   "화학2 1-3단원 모의고사",
    "j0":        "조준모의고사 0회",
}


def exams() -> list[dict]:
    return json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))


def cohort_alias() -> dict[str, str]:
    source = (ROOT / "final.html").read_text(encoding="utf-8")
    block = source.split("const COHORT_ALIAS=", 1)[1].split("};", 1)[0] + "}"
    return json.loads(re.sub(r"'", '"', block))


def build() -> dict[str, list[str]]:
    live = exams()
    out: dict[str, list[str]] = {}
    for exam in live:
        titles = [exam["title"]] + HISTORY.get(exam["id"], [])
        # 이 시험으로 합쳐진 옛 id 의 제목도 함께 인정한다
        for gone, kept in MERGED.items():
            if kept == exam["id"]:
                titles += HISTORY.get(gone, [])
        seen, uniq = set(), []
        for t in titles:
            if t and t not in seen:
                seen.add(t)
                uniq.append(t)
        out[exam["id"]] = uniq
    # 없앤 id 로 물어봐도 남긴 시험의 행이 나오게 한다
    for gone, kept in MERGED.items():
        if kept in out:
            out[gone] = out[kept]
    # index.html 의 옛 시험들(exams.json 에 없다). 앞에 두어 눈에 띄게 한다.
    return {**{k: [v] for k, v in LEGACY.items()}, **out}


def render(table: dict[str, list[str]]) -> str:
    width = max(len(k) for k in table) + 3
    lines = [BEGIN]
    for key, titles in table.items():
        value = json.dumps(titles, ensure_ascii=False).replace('"', "'").replace("', '", "', '")
        lines.append(f"  {(repr(key).replace(chr(34), chr(39)) + ':').ljust(width)} {value},")
    lines.append(END)
    return "\n".join(lines)


def main() -> int:
    table = build()
    block = render(table)
    source = GS.read_text(encoding="utf-8")
    start = source.index(BEGIN)
    stop = source.index("\n" + END, start) + len("\n" + END)
    current = source[start:stop]

    if "--write" in sys.argv[1:]:
        GS.write_text(source[:start] + block + source[stop:], encoding="utf-8")
        print(f"EXAM_TITLES {len(table)}개 항목을 새로 적었다.")
        return 0

    print(block)
    if current.strip() == block.strip():
        print(f"\nPASS 파일과 일치 ({len(table)}개 항목)")
        return 0
    print("\nFAIL 파일의 EXAM_TITLES 가 시험 목록과 어긋난다. --write 로 갱신한다.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
