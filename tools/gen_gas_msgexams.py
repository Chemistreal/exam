#!/usr/bin/env python3
"""`AppsScript-Code.gs` 의 MSG_EXAMS 를 `exams.json` 의 영역 데이터로 만든다.

왜 필요한가
-----------
성적표 문자에는 "이번 시험은 {범위}에서 골고루 물었습니다" 라는 자리가 있다.
그 {범위} 는 MSG_EXAMS[제목].topic 에서 온다. 그런데 표에 들어 있는 시험이
**38개 중 2개**뿐이라, 나머지 36개는 전부 이렇게 나갔다.

    이번 시험은 화학 개념과 문제 해결에서 골고루 물었습니다.

무엇을 물었는지 알려 주겠다고 해 놓고 아무것도 말하지 않는 문장이다.
그런데 회차별 영역 데이터는 이미 다 있다 — exams.json 의 `area` 에 문항마다
개념 영역이 붙어 있고, 38개 회차 전부 문항 수만큼 채워져 있다.

무엇을 담는가
-------------
문항이 많은 영역 순으로 골라 읽을 수 있게 잇는다. 몇 개까지 넣을지는
`TOP` 과 `COVER` 로 정한다 — 너무 적으면 시험을 대표하지 못하고, 너무 많으면
문자 한 줄이 영역 나열로 뒤덮인다.

    'JMChC 모의고사 6회': { topic: '쌍극자모멘트·산화환원반응·반응성·아미노산', mode: 'perc' }

`mode` 는 손대지 않는다. 'tier'(수상권 화법)로 적어 둔 회차는 선생님이 그렇게
정한 것이므로 기존 값을 그대로 옮긴다. 표에 없던 회차는 'perc'(백분위 화법).

사용:
    python3 tools/gen_gas_msgexams.py            # 만들어질 블록을 보여만 준다(어긋나면 1)
    python3 tools/gen_gas_msgexams.py --write    # AppsScript-Code.gs 에 써 넣는다
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_exam_titles import build as build_titles  # noqa: E402  EXAM_TITLES 와 같은 별칭을 쓴다

ROOT = Path(__file__).resolve().parents[1]
GS = ROOT / "AppsScript-Code.gs"
BEGIN = "var MSG_EXAMS = {"
END = "};"

TOP = 5            # 최대 몇 개 영역까지 적을지
COVER = 0.55       # 문항의 이 비율을 덮으면 그만 적는다
MIN_Q = 2          # 문항이 이보다 적은 영역은 대표성이 없다


def existing_modes(source: str) -> dict[str, str]:
    """이미 적혀 있는 mode 를 그대로 지킨다. 화법은 선생님이 정한 것이다."""
    block = source[source.index(BEGIN):source.index("\n" + END, source.index(BEGIN))]
    return dict(re.findall(r"'([^']+)':\s*\{[^}]*mode:\s*'(\w+)'", block))


def topic_of(exam: dict) -> str:
    area = exam.get("area") or []
    if len(area) != exam["nQ"]:
        return ""
    count = collections.Counter(a for a in area if a)
    picked, seen = [], 0
    for name, n in count.most_common():
        if len(picked) >= TOP or (picked and n < MIN_Q):
            break
        picked.append(name)
        seen += n
        if seen / exam["nQ"] >= COVER:
            break
    return "·".join(picked)


def build(source: str) -> dict[str, dict]:
    exams = json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))
    modes = existing_modes(source)
    titles = build_titles()

    out: dict[str, dict] = {}
    for exam in exams:
        topic = topic_of(exam)
        if not topic:
            print(f"  ! 영역 데이터가 없어 건너뜀: {exam['id']}", file=sys.stderr)
            continue
        # 옛 제목으로 쌓인 행도 같은 문구를 받아야 한다.
        for title in titles.get(exam["id"], [exam["title"]]):
            out[title] = {"topic": topic, "mode": modes.get(title, "perc")}
    # exams.json 에 없지만 표에 있던 회차(옛 kch* · 조준모의고사 0회)는 지키지 않으면
    # 문구가 통째로 사라진다. 원문 그대로 남긴다.
    for title, mode in modes.items():
        if title not in out:
            old = re.search(r"'" + re.escape(title) + r"':\s*\{\s*topic:\s*'([^']*)'", source)
            out[title] = {"topic": old.group(1) if old else "화학 개념과 문제 해결", "mode": mode}
    return out


def render(table: dict[str, dict]) -> str:
    lines = [BEGIN]
    for title, e in table.items():
        lines.append(f"  '{title}': {{ topic: '{e['topic']}', mode: '{e['mode']}' }},")
    lines.append(END)
    return "\n".join(lines)


def main() -> int:
    source = GS.read_text(encoding="utf-8")
    if BEGIN not in source:
        print("AppsScript-Code.gs 에 MSG_EXAMS 블록이 없다.", file=sys.stderr)
        return 2
    table = build(source)
    block = render(table)
    start = source.index(BEGIN)
    stop = source.index("\n" + END, start) + len("\n" + END)
    current = source[start:stop]

    if "--write" in sys.argv[1:]:
        GS.write_text(source[:start] + block + source[stop:], encoding="utf-8")
        print(f"MSG_EXAMS {len(table)}개 제목을 새로 적었다.")
        return 0

    print(block[:500] + ("\n…" if len(block) > 500 else ""))
    if current.strip() == block.strip():
        print(f"\nPASS 파일과 일치 ({len(table)}개 제목)")
        return 0
    print("\nFAIL MSG_EXAMS 가 시험 목록·영역 데이터와 어긋난다. --write 로 갱신한다.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
