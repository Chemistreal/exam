#!/usr/bin/env python3
"""`AppsScript-Code.gs` 의 EXAM_COHORT 를 `exams.json` + `cohort/baseline.json` 에서 만든다.

왜 필요한가
-----------
시트의 석차·백분위·전체누적인원은 **저장하는 그 순간**의 인원으로 한 번 계산되어
행에 박제된다. 그래서 먼저 채점한 학생은 43명 기준, 나중 학생은 44명 기준이 되고,
그 숫자 그대로 성적표 문자가 나간다. 같은 회차인데 학생마다 모집단이 다르다.

`recomputeExam` 이 이걸 다시 맞추는 함수인데, `_recomputeConfigFor` 가
'조준모의고사 0회' 에만 설정을 돌려주고 나머지는 null 이었다 — 즉 다른 회차는
재계산이 아예 돌지 않았다. 이 표가 그 빈자리를 채운다.

무엇이 들어가는가
-----------------
회차 **제목** → `{ q: 문항 수, base: [맞은 문항 수…] }`

시트는 시험을 제목으로 구분하므로(doPost 가 `d.exam = cur.title` 로 보낸다) 키가
제목이다. 제목은 바뀌므로('화올 2018' → 'KMChC 2018') EXAM_TITLES 와 **같은
별칭 목록**을 써서 옛 제목에도 같은 설정을 달아 둔다. 안 그러면 옛 이름으로
쌓인 행이 있는 회차는 재계산이 통째로 건너뛴다.

`base` 는 앱이 쓰는 것과 **같은 기준 응시 기록**이고, 단위도 같아야 한다 —
**맞은 문항 수**다.

[한 번 틀렸던 곳] 시트의 9번째 열 이름이 '원점수' 라서 원점수(180점 만점)인
줄 알고 3을 곱해 넣었다. 그런데 final.html 이 보내는 값은 `total: correct`,
즉 **맞은 문항 수**다(열 이름만 '원점수'다). 3을 곱한 기준 기록과 맞은 문항
수로 저장된 학생을 한 줄에 세우면 학생이 무조건 꼴찌가 된다 — 화면은 3/15,
문자는 12/15 라고 말했다. 단위가 어긋나면 조용히 틀린 숫자가 나간다.

'조준모의고사 0회'(J0_BASE_TOTALS)만 원점수 단위다. 그건 옛 index.html 이
원점수를 보내던 시험이라 그대로 둔다 — 회차가 다르니 섞이지 않는다.

기준 기록이 없는 회차도 `base: []` 로 표에 넣는다. 문항 수(q)가 필요하고,
표에 없으면 재계산이 통째로 건너뛰기 때문이다(50문항 회차가 6개 있다).

사용:
    python3 tools/gen_gas_cohort.py            # 만들어질 블록을 보여만 준다(어긋나면 1)
    python3 tools/gen_gas_cohort.py --write    # AppsScript-Code.gs 에 써 넣는다
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_exam_titles import build as build_titles  # noqa: E402  EXAM_TITLES 와 같은 별칭을 쓴다

ROOT = Path(__file__).resolve().parents[1]
GS = ROOT / "AppsScript-Code.gs"
BEGIN = "var EXAM_COHORT = {"
END = "};"

def check_unit() -> None:
    """final.html 이 시트로 보내는 값이 아직도 '맞은 문항 수' 인지 확인한다.

    이 한 줄이 바뀌면(예: 감점 반영 원점수를 보내도록) 기준 기록의 단위도 같이
    바꿔야 한다. 말없이 어긋나면 석차가 통째로 틀리므로 여기서 멈춘다."""
    source = (ROOT / "final.html").read_text(encoding="utf-8")
    if "total:correct,max:total" not in source.replace(" ", ""):
        raise SystemExit(
            "final.html 이 시트로 보내는 값의 형태가 바뀌었다.\n"
            "  기준 기록(base)은 '맞은 문항 수' 단위다. payload 의 total 이 무엇인지\n"
            "  확인하고 단위를 맞춘 뒤 이 검사를 갱신해야 한다.")


def build() -> dict[str, dict]:
    check_unit()
    exams = json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))
    base_path = ROOT / "cohort" / "baseline.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))["exams"] if base_path.exists() else {}
    titles = build_titles()

    out: dict[str, dict] = {}
    for exam in exams:
        scores: list[int] = []
        rec = base.get(exam["id"])
        if rec:
            # `miss`(채점 제외)가 있으면 여태 통째로 건너뛰었다 — "앱은 그
            # 문항을 빼고 세는데 기준 기록은 전 문항으로 셌다" 는 이유였다.
            # **지금은 안 그렇다.** 앱의 allc() 는 miss 를 voided 와 똑같이
            # 전원정답으로 보고 분모(nQ)에서도 빼지 않는다 —
            # tests/allcorrect.js 가 그 약속을 지킨다("빼지 않고 더한다").
            # 기준 기록 쪽도 정답 행에 숫자가 없는 문항(전원정답·문제삭제)은
            # 누구나 맞은 것으로 센다. 두 쪽이 같은 단위다.
            #
            # 건너뛰면 그 회차만 문자에 석차가 안 실린다 — 화면은 말하는데
            # 문자는 말하지 않는 상태가 된다. hwol-2021(57명)이 그랬다.
            # 대신 **넘치는지**만 본다. 맞은 개수가 문항 수를 넘으면 단위가
            # 어긋난 것이니 그때는 싣지 않는다(3을 곱한 값이 섞인 경우).
            over = sorted({int(k) for k in rec["hist"] if int(k) > exam["nQ"]})
            if over:
                print(f"  ! 기준 기록을 건너뜀(맞은 개수 {over[:3]} 가 문항 수 "
                      f"{exam['nQ']} 를 넘는다): {exam['id']}", file=sys.stderr)
            else:
                for correct, count in sorted(rec["hist"].items(), key=lambda kv: int(kv[0])):
                    scores += [int(correct)] * int(count)
        for title in titles.get(exam["id"], [exam["title"]]):
            out[title] = {"q": exam["nQ"], "base": scores}
    return out


def render(table: dict[str, dict]) -> str:
    lines = [BEGIN]
    for title, e in table.items():
        base = ",".join(str(v) for v in e["base"])
        lines.append(f"  '{title}': {{ q: {e['q']}, base: [{base}] }},")
    lines.append(END)
    return "\n".join(lines)


def main() -> int:
    table = build()
    block = render(table)
    source = GS.read_text(encoding="utf-8")

    if BEGIN not in source:
        print("AppsScript-Code.gs 에 EXAM_COHORT 블록이 없다. 먼저 자리를 만들어야 한다.",
              file=sys.stderr)
        return 2
    start = source.index(BEGIN)
    stop = source.index("\n" + END, start) + len("\n" + END)
    current = source[start:stop]

    withbase = sum(1 for e in table.values() if e["base"])
    people = sum(len(e["base"]) for e in table.values())

    if "--write" in sys.argv[1:]:
        GS.write_text(source[:start] + block + source[stop:], encoding="utf-8")
        print(f"EXAM_COHORT {len(table)}개 제목(기준 기록 {withbase}개 · {people}명)을 새로 적었다.")
        return 0

    print(block[:400] + ("\n…" if len(block) > 400 else ""))
    if current.strip() == block.strip():
        print(f"\nPASS 파일과 일치 ({len(table)}개 제목 · 기준 기록 {people}명)")
        return 0
    print("\nFAIL EXAM_COHORT 가 시험 목록·기준 기록과 어긋난다. --write 로 갱신한다.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
