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
회차 **제목** → `{ q: 문항 수, base: [원점수…] }`

시트는 시험을 제목으로 구분하므로(doPost 가 `d.exam = cur.title` 로 보낸다) 키가
제목이다. 제목은 바뀌므로('화올 2018' → 'KMChC 2018') EXAM_TITLES 와 **같은
별칭 목록**을 써서 옛 제목에도 같은 설정을 달아 둔다. 안 그러면 옛 이름으로
쌓인 행이 있는 회차는 재계산이 통째로 건너뛴다.

`base` 는 앱이 쓰는 것과 **같은 기준 응시 기록**이다(cohort/baseline.json).
앱은 맞은 문항 수로 세고 시트는 원점수로 세므로 3을 곱해 둔다. JMChC 는
오답 감점이 없어(finalPenalty=0) 원점수가 정확히 맞은 문항 수 × 3 이다.
이게 어긋나면 화면의 석차와 문자의 석차가 서로 다른 말을 한다.
감점이 있는 회차는 그 등식이 깨지므로 기준 기록을 싣지 않는다.

기준 기록이 없는 회차도 `base: []` 로 표에 넣는다. 문항 수(q)가 필요하고,
표에 없으면 재계산이 통째로 건너뛰기 때문이다(50문항 회차가 6개 있다).

사용:
    python3 tools/gen_gas_cohort.py            # 만들어질 블록을 보여만 준다(어긋나면 1)
    python3 tools/gen_gas_cohort.py --write    # AppsScript-Code.gs 에 써 넣는다
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_exam_titles import build as build_titles  # noqa: E402  EXAM_TITLES 와 같은 별칭을 쓴다

ROOT = Path(__file__).resolve().parents[1]
GS = ROOT / "AppsScript-Code.gs"
BEGIN = "var EXAM_COHORT = {"
END = "};"

PER_Q = 3          # 문항당 배점


def no_penalty_groups() -> set[str]:
    """final.html 의 finalPenalty 가 0 을 주는 그룹. 한쪽만 고치면 어긋나므로 읽어 온다."""
    source = (ROOT / "final.html").read_text(encoding="utf-8")
    line = re.search(r"function finalPenalty\(exam\)\{[^}]*\}", source)
    if not line:
        raise SystemExit("final.html 에서 finalPenalty 를 찾지 못했다.")
    groups = set(re.findall(r"g===?'([^']+)'", line.group(0)))
    if not groups:
        raise SystemExit("finalPenalty 에서 감점 없는 그룹을 읽지 못했다.")
    return groups


def build() -> dict[str, dict]:
    exams = json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))
    base_path = ROOT / "cohort" / "baseline.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))["exams"] if base_path.exists() else {}
    titles = build_titles()
    free = no_penalty_groups()

    out: dict[str, dict] = {}
    for exam in exams:
        scores: list[int] = []
        rec = base.get(exam["id"])
        if rec:
            if exam.get("group") not in free:
                # 감점이 있는 회차는 원점수 ≠ 맞은 문항 수 × 3 이라 그대로 못 쓴다.
                print(f"  ! 기준 기록을 건너뜀(감점 있는 회차): {exam['id']}", file=sys.stderr)
            else:
                for correct, count in sorted(rec["hist"].items(), key=lambda kv: int(kv[0])):
                    scores += [int(correct) * PER_Q] * int(count)
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
