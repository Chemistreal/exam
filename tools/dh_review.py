#!/usr/bin/env python3
"""집필된 파트 JSON을 검수용 압축 형식으로 출력.

화학적 정확성은 사람이 직접 본다. 판단에 필요한 정보(지문 전체·선택지 전체·정답·
해설 요지)는 남기고 군더더기만 덜어낸다.

사용: python3 tools/dh_review.py <examId> [시작] [끝] [--full]
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

WORK = Path(
    "/tmp/claude-0/-home-user-study64-report/"
    "2113474c-4485-592e-912d-e7d09ec51ec8/scratchpad/dh"
)
CI = ["", "①", "②", "③", "④"]


def load(exam_id: str) -> dict:
    merged: dict[str, dict] = {}
    for p in sorted(glob.glob(str(WORK / f"{exam_id}.part*.json"))):
        merged.update(json.loads(Path(p).read_text(encoding="utf-8")))
    return merged


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)
    exam_id = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    full = "--full" in sys.argv
    lo = int(args[0]) if args else 1
    hi = int(args[1]) if len(args) > 1 else 10**9

    data = load(exam_id)
    if not data:
        raise SystemExit(f"파트 파일 없음: {exam_id}")
    for key in sorted(data, key=lambda k: int(k)):
        n = int(key)
        if not (lo <= n <= hi):
            continue
        q = data[key]
        print(f"─{key}번[{q.get('concept','')}] 답{CI[q.get('answer',0)]}")
        print(f" Q {q.get('stem','')}")
        for i, c in enumerate(q.get("choices", []), 1):
            print(f" {CI[i]} {c}")
        if full:
            print(f" 해설 {q.get('explanation','')}")
    print(f"\n[{exam_id}] {len(data)}문항 로드")


if __name__ == "__main__":
    main()
