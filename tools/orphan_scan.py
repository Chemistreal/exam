#!/usr/bin/env python3
"""아무도 읽지 않는 자산을 찾는다.

`answers/` 와 `crops/` 는 `final.html` 이 **시험 id 로만** 찾아 읽는다
(`answers/<id>.json`, `crops/<id>/<문항>.png`). 그래서 시험 목록에서 어떤 id 를
빼면 그 폴더는 그 순간부터 아무도 열지 않는 죽은 파일이 된다. 파일이 남아
있어도 화면은 멀쩡하니 눈치채기 어렵고, 그대로 두면 저장소만 무거워진다.

실제로 화올 세 시험을 KMChC 로 합칠 때 `crops/kmchc-2018/` 등 180장이 그렇게
떠 버렸다(남긴 쪽과 바이트 단위로 같은 복사본이었다).

`donghyung/` 은 다르게 판정한다. 시험 목록에 없는 id 라도 `DH_SETS` 가 다른
시험의 문제풀로 끌어다 쓰고 있으면 살아 있는 파일이다.

지우지는 않는다. 무엇이 떠 있는지 알려 주고 명령만 찍어 준다. 실제로 같은
내용인지(남긴 쪽의 복사본인지) 한 번 보고 지우는 편이 안전하다.

사용:
    python3 tools/orphan_scan.py          # 목록만
    python3 tools/orphan_scan.py --strict # 떠 있는 게 있으면 종료 코드 1 (CI용)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "final.html").read_text(encoding="utf-8")


def live_exam_ids() -> set[str]:
    """살아 있는 시험 id 전부.

    ⚠ `exams.json` 만 보면 안 된다. 화면은 목록 **셋**을 읽는다
      (final.html:1019~1023) — exams.json · student-finals.json ·
      teacher-exams.json. 앞의 하나만 보던 시절 이 도구는 학생별 파이널
      서른한 회차를 통째로 「아무도 안 읽는 파일」로 몰아 `git rm` 명령을
      찍어 주고 있었다. 그 명령을 그대로 쳤으면 학생들이 보는 시험이
      다 사라진다.

      그런데 아무도 못 봤다. **이 도구가 그때 죽어 있었기 때문이다**
      (DH_SETS 의 끝 쉼표). 죽은 검사는 통과한 검사처럼 조용하다.
      새 목록이 생기면 여기에 반드시 더해야 한다."""
    out: set[str] = set()
    for name in ("exams.json", "student-finals.json", "teacher-exams.json"):
        path = ROOT / name
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        rows = raw.get("exams", []) if isinstance(raw, dict) else raw
        out.update(e["id"] for e in rows if isinstance(e, dict) and e.get("id"))
    return out


def dh_set_ids() -> set[str]:
    """DH_SETS 가 문제풀로 끌어다 쓰는 파일 이름까지 포함한다.

    ⚠ 자바스크립트 객체를 JSON 으로 읽는 자리다. 따옴표만 바꿔서는 안 된다 —
      JS 는 마지막 항목 뒤의 쉼표를 허용하고 JSON 은 안 한다. 실제로 그
      쉼표 하나 때문에 이 도구가 통째로 죽어 있었다(2026-09-09 에 잡았다).
      죽으면 「고아 파일 없음」이 아니라 **아무것도 못 잰 것**인데, 검사를
      한 바퀴 돌리기 전에는 그것이 안 보인다.
      같은 버그를 tests/final-cohort-alias.js 에서도 한 번 고쳤다."""
    block = SOURCE.split("const DH_SETS=", 1)[1].split("};", 1)[0] + "}"
    block = re.sub(r",(\s*[}\]])", r"\1", re.sub(r"'", '"', block))
    sets = json.loads(block)
    out: set[str] = set()
    for target, files in sets.items():
        out.add(target)
        out.update(files)
    return out


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def size_of(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def main() -> int:
    live = live_exam_ids()
    pooled = dh_set_ids()
    orphans: list[tuple[str, Path, int]] = []

    for path in sorted((ROOT / "answers").glob("*.json")):
        if path.stem not in live:
            orphans.append(("answers", path, size_of(path)))

    crops = ROOT / "crops"
    if crops.is_dir():
        for path in sorted(p for p in crops.iterdir() if p.is_dir()):
            if path.name not in live:
                orphans.append(("crops", path, size_of(path)))

    # donghyung 은 문제풀로 끌어다 쓰는 것까지 살아 있는 것으로 본다.
    # index.json 은 시험 id 가 아니라 개념 색인이다. `final.html` 이 선수 개념
    # 드릴에서 직접 받아 간다. 시험 id 로만 보면 고아로 잡혀 "지워라"가 나가는데,
    # 그대로 지우면 드릴이 죽는다.
    for path in sorted((ROOT / "donghyung").glob("*.json")):
        if path.stem.startswith("_") or path.name == "index.json":
            continue
        if path.stem not in live and path.stem not in pooled:
            orphans.append(("donghyung", path, size_of(path)))

    # ── 자를 먼저 잰다 ──────────────────────────────────────────────
    # 목록 하나를 놓치면 이 도구는 「지워라」를 **더 많이** 찍는다. 조용히
    # 틀리는 쪽이 위험하므로, 세어 보기 전에 자가 성한지부터 본다.
    for name in ("student-finals.json", "teacher-exams.json"):
        path = ROOT / name
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        rows = raw.get("exams", []) if isinstance(raw, dict) else raw
        ids = {e["id"] for e in rows if isinstance(e, dict) and e.get("id")}
        if ids and not (ids & live):
            print(f"FAIL {name} 의 시험 {len(ids)}개가 살아 있는 목록에 하나도 "
                  f"안 들어 있다 — live_exam_ids() 가 그 목록을 안 읽고 있다.")
            print("     이대로 두면 멀쩡한 시험을 지우라고 찍는다.")
            return 1

    print(f"시험 {len(live)}개 · 문제풀에 묶인 파일 {len(pooled)}개")
    if not orphans:
        print("PASS 떠 있는 자산 없음")
        return 0

    total = sum(size for _, _, size in orphans)
    print(f"\n아무도 읽지 않는 자산 {len(orphans)}개 · 합계 {human(total)}")
    for kind, path, size in orphans:
        rel = path.relative_to(ROOT)
        print(f"  [{kind:9}] {str(rel):34} {human(size):>8}")

    print("\n  지우기 전에 남긴 쪽과 같은 내용인지 확인:")
    print("      diff -rq crops/<없앤id> crops/<남긴id>")
    print("  확인했으면:")
    print("      git rm -r " + " ".join(str(p.relative_to(ROOT)) for _, p, _ in orphans))
    return 1 if ("--strict" in sys.argv[1:] or "--check" in sys.argv[1:]) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # `| head` 로 잘라 볼 때 역추적을 남기지 않는다
        sys.exit(0)
