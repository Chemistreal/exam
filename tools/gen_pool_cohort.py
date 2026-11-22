#!/usr/bin/env python3
"""같은 범위의 시험을 본 학생들과 **석차 모집단을 합친다** → `cohort/baseline.json`

왜
---
새로 들인 회차는 응시자가 몇 안 된다. 석차·백분위가 「3명 중 1등」 으로 나가면
학부모에게는 아무 말도 하지 않는 숫자다. 같은 단원 범위를 같은 60문항으로 본
옛 회차들에는 성적표 엑셀에서 옮긴 응시 기록이 수백 명씩 있다.

선생님 결정(2026-11-22): 화학1 1-3단원 총괄평가(심화반, kch1to3-s)의 성적은
**1-3단원 모의고사(kch1to3) 와 그 동형(kch1to3-b) 응시자까지 합산해서** 매긴다.

무엇을 합치고 무엇을 안 합치나
-------------------------------
  합친다    총점 분포(hist) — 석차 · 백분위 · 전체 인원 · 반석차
  안 합친다 문항별 정답자 수(qc · q) — 또래 정답률 · 선택지 분포.
            문항이 서로 다른 시험이라 3번 문항끼리 더하면 뜻이 없다.
            그 통계는 이 회차를 실제로 본 학생만으로 센다.

어디에 쓰이나
-------------
  · exams.json 의 `rankWith: [회차 id…]` 가 정본이다(한 곳에만 적는다).
  · 이 도구가 그 회차들의 기준 기록(hist)을 더해 `baseline.json` 에
    `{from: "pool", pool: [...], n, hist}` 로 적는다. 화면(final.html)은
    다른 회차와 똑같이 이 hist 를 모집단으로 읽는다.
  · 앱으로 채점해 시트에 쌓인 줄은 기준 기록에 안 들어 있다. 그건 앱스크립트가
    합친다 — `EXAM_COHORT[제목].pool`(tools/gen_gas_cohort.py 가 같은
    rankWith 로 만든다)을 보고 재계산·`?action=cohort` 가 그 회차들의 줄도 센다.
  · 밤마다 도는 기준 기록 자동 갱신(rebuildBaseline)은 `from: "pool"` 인
    회차를 건드리지 않는다(_baselineKeepWhy_). 시트만으로 덮으면 합친 수백 명이
    사라지고, 시트 줄은 위에서 따로 세므로 두 번 세어진다.

사용:
    python3 tools/gen_pool_cohort.py            # 무엇이 적히나
    python3 tools/gen_pool_cohort.py --write    # baseline.json 에 적는다
    python3 tools/gen_pool_cohort.py --check    # 어긋나면 종료 코드 1 (CI)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMS = ROOT / "exams.json"
BASE = ROOT / "cohort" / "baseline.json"


def build(exams: list[dict], base: dict) -> dict[str, dict]:
    by_id = {e["id"]: e for e in exams}
    out: dict[str, dict] = {}
    for exam in exams:
        members = exam.get("rankWith")
        if not members:
            continue
        hist: dict[int, int] = {}
        for mid in members:
            m = by_id.get(mid)
            if m is None:
                raise SystemExit(f"{exam['id']}.rankWith 의 {mid} 가 시험 목록에 없다")
            # 문항 수가 다르면 맞은 개수끼리 견줄 수 없다 — 60문항의 40과 50문항의 40은 다른 점수다.
            if m["nQ"] != exam["nQ"]:
                raise SystemExit(f"{exam['id']}({exam['nQ']}문항) 와 {mid}({m['nQ']}문항) 는 문항 수가 달라 합칠 수 없다")
            if m.get("rankWith"):
                raise SystemExit(f"{mid} 도 rankWith 를 가졌다 — 합친 것을 또 합치면 같은 사람이 두 번 들어간다")
            rec = base.get(mid) or {}
            if not rec.get("hist"):
                raise SystemExit(f"{mid} 에 기준 기록(hist)이 없어 합칠 것이 없다")
            if rec.get("from") in ("sheet", "pool"):
                # 시트에서 만든 기록은 시트 줄과 같은 사람들이다. 앱스크립트가 시트 줄을 따로
                # 더하므로 여기서도 넣으면 두 번 센다.
                raise SystemExit(f"{mid} 의 기준 기록은 from={rec.get('from')} 이라 합치면 두 번 센다")
            for k, v in rec["hist"].items():
                if int(k) > exam["nQ"]:
                    raise SystemExit(f"{mid} 의 기준 기록에 문항 수({exam['nQ']})를 넘는 점수 {k} 가 있다")
                hist[int(k)] = hist.get(int(k), 0) + int(v)
        own = base.get(exam["id"]) or {}
        if own and own.get("from") != "pool" and (own.get("hist") or own.get("qc")):
            # 이 회차 자신의 엑셀 기록이 생기면 그것도 더해야 한다. 지금은 없다 — 생기면 사람이 정한다.
            raise SystemExit(f"{exam['id']} 에 자체 기준 기록이 있다(from={own.get('from')}). "
                             "합칠지 사람이 정한 뒤 이 도구를 고친다")
        out[exam["id"]] = {
            "n": sum(hist.values()),
            "hist": {str(k): hist[k] for k in sorted(hist)},
            "from": "pool",
            "pool": list(members),
            # ⚠ 까닭을 여기 글로 적지 않는다. baseline.json 에는 한글이 한 자도 없어야
            #   한다 — 이름이 섞여 들어오면 바로 잡으려는 자(tests/rank-baseline.js)가 있다.
            #   까닭은 이 파일 머리와 exams.json 의 rankWith 가 말한다.
        }
    return out


def main() -> int:
    exams = json.loads(EXAMS.read_text(encoding="utf-8"))
    doc = json.loads(BASE.read_text(encoding="utf-8"))
    base = doc["exams"]
    want = build(exams, base)

    # rankWith 를 지운 회차의 합친 기록은 걷어 낸다 — 남겨 두면 화면은 계속 합쳐서 센다.
    stale = [k for k, v in base.items() if v.get("from") == "pool" and k not in want]
    diff = [k for k, v in want.items() if base.get(k) != v]

    for k, v in want.items():
        print(f"  {k}: {' + '.join(v['pool'])} → {v['n']}명")
    for k in stale:
        print(f"  {k}: rankWith 가 없어졌다 — 합친 기록을 걷어 낸다")

    if "--write" in sys.argv[1:]:
        for k in stale:
            del base[k]
        base.update(want)
        BASE.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"cohort/baseline.json 에 적었다 (합친 회차 {len(want)}개 · 걷어 낸 것 {len(stale)}개)")
        return 0
    if diff or stale:
        print(f"FAIL 합친 기준 기록이 어긋난다: {diff + stale} — python3 tools/gen_pool_cohort.py --write")
        return 1
    print(f"PASS 합친 기준 기록이 최신이다 ({len(want)}개 회차)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
