#!/usr/bin/env python3
"""집필된 동형문제(schemaVersion 2, strategy=original-authored) 구조 검증.

화학적 정확성은 사람이/검수 에이전트가 보지만, 구조적 결함은 여기서 전부 걸러낸다.
사용: python3 tools/dh_validate.py donghyung/<examId>.json [...]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 생성 실패 흔적 — 재집필본에는 절대 있으면 안 된다
PLACEHOLDER = re.compile(
    r"(?:렌더|렌더링|추출|복원|원본)[^\n]{0,30}?누락|누락[^\n]{0,30}?(?:렌더|렌더링|추출|복원)|렌더\s*실패|추출\s*실패|복원되지\s*않"
    r"|TODO|원본 채점표|원본서"
)
CIRCLED = re.compile(r"[①②③④]")


def check_entry(number: str, q: dict) -> list[str]:
    errs: list[str] = []
    stem = str(q.get("stem") or "").strip()
    choices = q.get("choices") or []
    answer = q.get("answer")
    expl = str(q.get("explanation") or "").strip()

    if not stem:
        errs.append("stem 비어 있음")
    if len(stem) < 12:
        errs.append("stem 이 너무 짧음")
    if len(choices) != 4:
        errs.append(f"선택지 4개가 아님({len(choices)})")
    for i, c in enumerate(choices, 1):
        if not str(c or "").strip():
            errs.append(f"선택지 {i} 비어 있음")
    if len({str(c).strip() for c in choices}) != len(choices):
        errs.append("선택지 중복")
    if answer not in (1, 2, 3, 4):
        errs.append(f"정답 번호 이상({answer})")
    if not expl:
        errs.append("해설 비어 있음")
    if PLACEHOLDER.search(stem + expl):
        errs.append("플레이스홀더/원본 참조 문구 포함")
    # 선택지 본문에 ①②③④ 를 다시 넣지 않는다(렌더 시 중복)
    for i, c in enumerate(choices, 1):
        if CIRCLED.search(str(c)):
            errs.append(f"선택지 {i}에 원문자 중복")
    # 오답마다 오개념 설명이 있어야 한다
    mis = q.get("misconceptions") or {}
    for opt in range(1, 5):
        if opt == answer:
            continue
        if not str(mis.get(str(opt)) or "").strip():
            errs.append(f"오답 {opt} 오개념 설명 없음")
    if not str(q.get("concept") or "").strip():
        errs.append("concept 없음")
    if q.get("origin") != "authored":
        errs.append("origin != authored")
    # 기출 복제 방지: 원본 시험/문항 참조 필드가 남아 있으면 안 된다
    for banned in ("sourceExamId", "sourceQuestion", "sourceExamTitle", "matchLevel"):
        if q.get(banned):
            errs.append(f"기출 참조 필드 잔존: {banned}")
    return errs


def main() -> None:
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    # 낱개로만 부를 수 있어서 CI 에 걸 수가 없었다. 걸려 있지 않으니 아무도
    # 안 돌렸고, 보기 넷이 모두 '①' 인 문항이 그대로 나가 있었다(hwol-2011
    # 59번 — 문두에 적어 둔 보기를 choices 로 옮기지 않은 자리다).
    if "--all" in sys.argv[1:]:
        skip = {"index.json", "_template.json"}
        paths = sorted(str(x) for x in (ROOT / "donghyung").glob("*.json")
                       if x.name not in skip)
    if not paths:
        print(__doc__)
        raise SystemExit(1)
    total = bad = 0
    for p in paths:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        if data.get("strategy") != "original-authored":
            print(f"[{p}] strategy 가 original-authored 가 아님")
            raise SystemExit(1)
        questions = data.get("questions", {})
        for number in sorted(questions, key=lambda k: int(k)):
            total += 1
            errs = check_entry(number, questions[number])
            if errs:
                bad += 1
                print(f"[{Path(p).name} {number}번] " + " / ".join(errs))
    print(f"{'FAIL' if bad else 'PASS'} 검증: {total}문항 중 결함 {bad}건")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
