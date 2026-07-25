#!/usr/bin/env python3
"""동형문제 재집필용 입력 매니페스트 생성.

각 문항이 '무엇을 묻는 문제였는지'(개념·학습 포인트·함정)만 뽑아낸다.
원문 지문·선택지는 담지 않는다 — 기출을 복제하지 않고 같은 개념의
독자 문항을 새로 집필하기 위한 입력이다.

사용: python3 tools/dh_manifest.py <examId> [시작번호] [끝번호]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(exam_id: str, lo: int = 1, hi: int | None = None) -> list[dict]:
    answers = json.loads(
        (ROOT / "answers" / f"{exam_id}.json").read_text(encoding="utf-8")
    )
    questions = answers.get("questions", answers)
    numbers = sorted(questions, key=lambda k: int(k))
    out = []
    for key in numbers:
        n = int(key)
        if n < lo or (hi is not None and n > hi):
            continue
        q = questions[key]
        out.append(
            {
                "number": n,
                "concept": q.get("concept") or "",
                "area": q.get("area") or "",
                "learningPoint": q.get("learningPoint") or "",
                # 원 문항이 노린 함정 — 새 문항의 오답 선택지 설계에 쓴다
                "trap": q.get("misconception") or "",
            }
        )
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)
    exam_id = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else None
    print(json.dumps(build(exam_id, lo, hi), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
