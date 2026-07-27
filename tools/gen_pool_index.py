#!/usr/bin/env python3
"""2400문항을 개념으로 찾을 수 있게 색인을 만든다 → `donghyung/index.json`

지금 동형문제는 `시험 → 문항번호` 로만 찾는다. 그래서 '몰 개념을 틀린 학생에게
몰 문제를 더 주기'가 안 된다. 그 학생이 푼 시험 안에 마침 몰 문항이 또 있어야만
가능하다. 2400문항이 시험 칸막이에 갇혀 있는 셈이다.

색인은 **어디에 무엇이 있는지만** 담는다(지문·해설은 담지 않는다). 그래야
30KB 남짓으로 끝나고, 실제 문항은 필요할 때 그 시험 파일만 불러오면 된다.
서비스워커가 그 파일들을 캐시하므로 두 번째부터는 네트워크도 타지 않는다.

분류는 두 층이다.
  concept  집필할 때 붙인 세부 개념(597가지). 정확하지만 303가지는 문항이 하나뿐이라
           이것만으로는 문제를 모으지 못한다.
  broad    final.html 의 RX 대분류 16가지. RXMAP 으로 area 를 접어서 얻는다.
           성적표가 이미 쓰는 말이라 새 용어를 만들지 않는다.

세부 개념으로 먼저 찾고, 모자라면 대분류로 넓힌다.

사용:
    python3 tools/gen_pool_index.py           # 만들어질 내용을 요약해 보여준다
    python3 tools/gen_pool_index.py --write   # donghyung/index.json 에 쓴다
    python3 tools/gen_pool_index.py --check   # 파일이 최신인지만 확인 (CI용)
"""

from __future__ import annotations

import collections
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "donghyung" / "index.json"
SCHEMA = 1


def read_map(name: str) -> dict[str, str]:
    """final.html 의 RXMAP 을 그대로 읽는다(분류 기준이 갈라지지 않게)."""
    source = (ROOT / "final.html").read_text(encoding="utf-8")
    body = re.search(rf"const {name}=\{{(.*?)\}};", source, re.S)
    if not body:
        raise SystemExit(f"{name} 을 final.html 에서 찾지 못했다")
    return dict(re.findall(r"'([^']*)'\s*:\s*'([^']*)'", body.group(1)))


def rx_keys() -> set[str]:
    source = (ROOT / "final.html").read_text(encoding="utf-8")
    body = re.search(r"const RX=\{(.*?)\n\};", source, re.S)
    return set(re.findall(r"'([^']+)':\{", body.group(1)))


def build() -> dict:
    rxmap, broad_keys = read_map("RXMAP"), rx_keys()

    def broaden(area: str) -> str:
        if area in broad_keys:
            return area
        return rxmap.get(area, area)

    by_concept: dict[str, list[str]] = collections.defaultdict(list)
    by_broad: dict[str, list[str]] = collections.defaultdict(list)
    total = 0
    unmapped: collections.Counter[str] = collections.Counter()

    for path in sorted(glob.glob(str(ROOT / "donghyung" / "*.json"))):
        if Path(path).stem in ("index", "_template"):
            continue
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("strategy") != "original-authored":
            continue
        exam_id = Path(path).stem
        for number, question in data["questions"].items():
            ref = f"{exam_id}:{number}"
            concept = (question.get("concept") or "").strip()
            area = (question.get("area") or "").strip()
            broad = broaden(area)
            if concept:
                by_concept[concept].append(ref)
            if broad:
                by_broad[broad].append(ref)
                if broad not in broad_keys:
                    unmapped[area] += 1
            total += 1

    return {
        "schemaVersion": SCHEMA,
        "note": "동형문제를 개념으로 찾기 위한 색인. 지문·해설은 담지 않는다. "
                "'<시험id>:<문항번호>' 로 가리키고, 실제 문항은 donghyung/<시험id>.json 에서 읽는다. "
                "tools/gen_pool_index.py 로 다시 만든다.",
        "total": total,
        "broad": {k: sorted(v) for k, v in sorted(by_broad.items())},
        "concept": {k: sorted(v) for k, v in sorted(by_concept.items())},
        "_unmapped": dict(unmapped.most_common()),
    }


def main() -> int:
    index = build()
    args = sys.argv[1:]

    if "--write" in args:
        OUT.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{OUT.relative_to(ROOT)} 에 {index['total']}문항 색인을 썼다 "
              f"({OUT.stat().st_size/1024:.0f}KB)")
        return 0

    if "--check" in args:
        if not OUT.exists():
            print("FAIL donghyung/index.json 이 없다. --write 로 만든다.")
            return 1
        current = json.loads(OUT.read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(index, ensure_ascii=False))
        if current == fresh:
            print(f"PASS 색인이 최신 ({index['total']}문항 · "
                  f"대분류 {len(index['broad'])} · 세부 {len(index['concept'])})")
            return 0
        print("FAIL 색인이 문항 데이터와 어긋난다. tools/gen_pool_index.py --write 로 갱신한다.")
        return 1

    print(f"문항 {index['total']}개")
    print(f"대분류 {len(index['broad'])}가지:")
    for key, refs in sorted(index["broad"].items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(refs):5}  {key}")
    thin = [k for k, v in index["concept"].items() if len(v) == 1]
    print(f"\n세부 개념 {len(index['concept'])}가지 (문항이 하나뿐인 것 {len(thin)}가지)")
    if index["_unmapped"]:
        print("\nRX 대분류로 접히지 않은 area (RXMAP 에 없다):")
        for area, n in list(index["_unmapped"].items())[:15]:
            print(f"  {n:5}  {area}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
