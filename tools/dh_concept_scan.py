#!/usr/bin/env python3
"""원 DB의 `concept` 라벨에서 오타 후보를 찾는다.

concept 은 화면에 표시되지 않는 메타데이터지만 재집필본마다 그대로 복사되므로,
오타를 원본에서 끊어야 한다. 실제로 계싼(계산)·워자(원자)·생서엔탈피(생성엔탈피)·
빛엔어지(빛에너지)·에탈올(에탄올) 같은 오타가 섞여 있었다.

정상적인 화학 용어는 서로 음절을 많이 공유하므로, **전체에서 두 번 이하로만
쓰인 음절**을 포함한 값이 오타 후보다. 고유명사(갈바니·벤젠·톰슨 등)도 함께
걸리니 사람이 최종 판단한다.

사용: python3 tools/dh_concept_scan.py
"""

from __future__ import annotations

import collections
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    values: collections.Counter[str] = collections.Counter()
    syllables: collections.Counter[str] = collections.Counter()
    for path in sorted(glob.glob(str(ROOT / "answers" / "*.json"))):
        questions = json.loads(Path(path).read_text(encoding="utf-8"))["questions"]
        for question in questions.values():
            concept = (question.get("concept") or "").strip()
            if not concept:
                continue
            values[concept] += 1
            for char in set(concept):
                if "가" <= char <= "힣":
                    syllables[char] += 1

    rare = {char for char, count in syllables.items() if count <= 2}
    flagged = [(v, "".join(sorted(set(v) & rare))) for v in sorted(values) if set(v) & rare]
    print(f"고유 concept {len(values)}개 중 후보 {len(flagged)}개")
    for value, chars in flagged:
        print(f"  {value:24} 희귀음절:{chars}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # `| head` 로 잘라 볼 때 역추적을 남기지 않는다
        pass
