#!/usr/bin/env python3
"""한 시험 안에서 서로 같은 문항이 된 쌍을 찾는다.

파트를 나눠 병렬로 집필하면 집필자끼리 상대 파트를 볼 수 없어서, 같은 개념이
두 파트에 배정됐을 때 사실상 같은 문항이 나온다. 실제로 donghyung-3 에서
2번과 31번(등전자 이온 반지름 순서), 28번과 39번(콕으로 연결한 두 용기 혼합)이
그렇게 겹쳤다. 병합 직후·검수 전에 한 번 돌린다.

지문의 문자 3-그램 자카드 유사도로 재고, concept 또는 area 가 같은 쌍은
따로 표시한다. 화학 문항은 숫자·물질명이 달라도 묻는 구조가 같으면 3-그램이
많이 겹친다.

사용: python3 tools/dh_dupe_scan.py <examId> [임계값]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 수치·기호는 문항마다 당연히 다르므로 지우고 문장 뼈대만 비교한다.
NOISE = re.compile(r"[0-9.,()\[\]{}·×→⇌=<>+\-/％%\s]+")


def trigrams(text: str) -> set[str]:
    flat = NOISE.sub("", text)
    return {flat[i : i + 3] for i in range(len(flat) - 2)}


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)
    exam_id = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.30

    questions = json.loads(
        (ROOT / "donghyung" / f"{exam_id}.json").read_text(encoding="utf-8")
    )["questions"]
    grams = {k: trigrams(v.get("stem", "")) for k, v in questions.items()}

    hits = []
    keys = sorted(questions, key=int)
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            union = grams[a] | grams[b]
            if not union:
                continue
            score = len(grams[a] & grams[b]) / len(union)
            same_concept = questions[a].get("concept") == questions[b].get("concept")
            if score >= threshold or same_concept:
                hits.append((score, a, b, same_concept))

    hits.sort(reverse=True)
    print(f"[{exam_id}] 검사 쌍 {len(keys) * (len(keys) - 1) // 2}개 · 후보 {len(hits)}개")
    for score, a, b, same_concept in hits:
        mark = "개념동일" if same_concept else "        "
        print(f"  {a:>2}–{b:<2} 유사도 {score:.2f} {mark}")
        for key in (a, b):
            head = questions[key].get("stem", "").splitlines()[0][:58]
            print(f"      {key:>2}[{questions[key].get('concept','')}] {head}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # `| head` 로 잘라 볼 때 역추적을 남기지 않는다
        pass
