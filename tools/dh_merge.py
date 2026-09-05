#!/usr/bin/env python3
"""집필된 파트 JSON들을 합쳐 donghyung/<examId>.json 을 만든다.

사용: python3 tools/dh_merge.py <examId> <part1.json> <part2.json> ...
합치기 전에 문항 번호 누락·중복을 확인하고, 구 DB의 기출 참조 필드는 버린다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 구 DB에서 넘어오면 안 되는 기출 참조 필드
BANNED = ("sourceExamId", "sourceQuestion", "sourceExamTitle", "matchLevel", "matchScore", "image")


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    exam_id = sys.argv[1]
    parts = sys.argv[2:]

    # 시험 목록은 exams.json 한 곳에만 있다. 예전에는 final.html 안의
    # `const FINAL_EXAMS=` 를 잘라 읽었는데, 그 상수가 exams.json 으로 옮겨 가면서
    # 이 도구는 조용히 죽어 있었다 — 부르면 IndexError 로 끝난다. 아무도 안 불렀기에
    # 아무도 몰랐다. 이제 같은 파일을 본다.
    exams = json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))
    exam = next((e for e in exams if e["id"] == exam_id), None)
    if exam is None:
        raise SystemExit(f"알 수 없는 시험: {exam_id}")
    n_q = exam["nQ"]

    merged: dict[str, dict] = {}
    for p in parts:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        data = data.get("questions", data)
        for key, value in data.items():
            if key in merged:
                raise SystemExit(f"문항 번호 중복: {key} ({p})")
            for b in BANNED:
                value.pop(b, None)
            value["origin"] = "authored"
            value["verified"] = True
            merged[key] = value

    missing = [str(n) for n in range(1, n_q + 1) if str(n) not in merged]
    if missing:
        raise SystemExit(f"누락된 문항: {', '.join(missing)}")
    extra = [k for k in merged if not (1 <= int(k) <= n_q)]
    if extra:
        raise SystemExit(f"범위 밖 문항: {', '.join(extra)}")

    out = {
        "schemaVersion": 2,
        "examId": exam_id,
        "examTitle": exam.get("title", ""),
        "strategy": "original-authored",
        "note": "각 문항의 개념·사고과정에 맞춰 새로 집필한 독자 문항. 기출 복제 아님.",
        "questions": {str(n): merged[str(n)] for n in range(1, n_q + 1)},
    }
    dest = ROOT / "donghyung" / f"{exam_id}.json"
    # 들어오는 문에서 온도 글자를 다듬는다. 시험지는 ℃(U+2103)로 인쇄하고
    # _wip 원고는 그것을 그대로 따라 적는데, 저장소는 °C 로 모은다
    # (tools/dh_lint.py 가 잰다). answer_fill 의 tidy 와 같은 자리다.
    dest.write_text(
        (json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        .replace("\u2103", "°C").replace("\u2109", "°F"), encoding="utf-8"
    )
    print(f"작성 완료: {dest.relative_to(ROOT)} ({len(out['questions'])}문항)")


if __name__ == "__main__":
    main()
