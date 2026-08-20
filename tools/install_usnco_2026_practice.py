#!/usr/bin/env python3
"""USNCO 2026 National Part I의 60문항 동형 연습문제를 설치한다.

대용량 JSON을 안전하게 전달하기 위해 .tmp-usnco-practice/chunk*.txt에
base64(gzip(JSON)) 조각으로 보관한 뒤 이 스크립트가 합쳐 검증하고
`donghyung/usnco-2026-natl-1.json`으로 만든다.

설치 후 임시 조각은 삭제한다. 이미 설치된 저장소에서 다시 실행해도 안전하다.
"""
from __future__ import annotations

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / ".tmp-usnco-practice"
OUT = ROOT / "donghyung" / "usnco-2026-natl-1.json"
TEST = ROOT / "tests" / "wrongbook-assets.py"
EXAM_ID = "usnco-2026-natl-1"


def validate(data: dict) -> None:
    if data.get("examId") != EXAM_ID:
        raise SystemExit("examId 불일치")
    if data.get("strategy") != "original-authored":
        raise SystemExit("strategy는 original-authored여야 한다")
    qs = data.get("questions") or {}
    if set(qs) != {str(i) for i in range(1, 61)}:
        raise SystemExit(f"동형문제 문항 수/번호 불일치: {len(qs)}")
    for i in range(1, 61):
        q = qs[str(i)]
        ans = q.get("answer")
        if ans not in (1, 2, 3, 4):
            raise SystemExit(f"{i}번 정답 범위 오류")
        if q.get("origin") != "authored" or q.get("verified") is not True:
            raise SystemExit(f"{i}번 authored/verified 오류")
        if len(q.get("choices") or []) != 4 or not all(str(x).strip() for x in q["choices"]):
            raise SystemExit(f"{i}번 선택지 오류")
        if not str(q.get("stem") or "").strip() or not str(q.get("explanation") or "").strip():
            raise SystemExit(f"{i}번 지문/해설 누락")
        need = {str(x) for x in range(1, 5) if x != ans}
        have = set((q.get("misconceptions") or {}).keys())
        if not need.issubset(have):
            raise SystemExit(f"{i}번 오답선지 해설 누락: {sorted(need-have)}")


def load_payload() -> dict:
    chunks = sorted(TMP.glob("chunk*.txt"), key=lambda p: int(p.stem.replace("chunk", "")))
    if not chunks:
        if OUT.exists():
            data = json.loads(OUT.read_text(encoding="utf-8"))
            validate(data)
            return data
        raise SystemExit("USNCO 동형문제 조각도 결과 파일도 없다")
    expected = [f"chunk{i}.txt" for i in range(1, 6)]
    if [p.name for p in chunks] != expected:
        raise SystemExit(f"동형문제 조각 불완전: {[p.name for p in chunks]}")
    packed = "".join(p.read_text(encoding="utf-8").strip() for p in chunks)
    raw = gzip.decompress(base64.b64decode(packed)).decode("utf-8")
    data = json.loads(raw)
    validate(data)
    return data


def patch_wrongbook_total() -> None:
    s = TEST.read_text(encoding="utf-8")
    if "assert seen == 2700" in s:
        return
    old = 'assert seen == 2640, f"문항 총합이 달라졌다: {seen} (기대 2640)"'
    if old not in s:
        raise SystemExit("wrongbook 총합 앵커를 찾지 못했다")
    note = (
        "#    2640 → 2700 : USNCO 2026 National Part I 60문항을 추가했다. 원문 크롭·상세 해설·\n"
        "#    독자 동형문제 60문항까지 모두 연결했다 (2026-08-20).\n"
    )
    s = s.replace(old, note + 'assert seen == 2700, f"문항 총합이 달라졌다: {seen} (기대 2700)"', 1)
    TEST.write_text(s, encoding="utf-8")


def main() -> int:
    data = load_payload()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    patch_wrongbook_total()

    # 설치가 끝난 대용량 전달 조각은 저장소에 남기지 않는다.
    if TMP.exists():
        for p in TMP.glob("chunk*.txt"):
            p.unlink()
        try:
            TMP.rmdir()
        except OSError:
            pass

    print("PASS USNCO 2026 동형 연습문제 60문항 설치 · 지문/선택지/정답/풀이/오개념 검증")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
