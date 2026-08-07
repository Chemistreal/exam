#!/usr/bin/env python3
"""`exams.json` 의 `solFull` 을 `answers/<id>.json` 에서 만든다.

왜 필요한가
-----------
회차마다 `sol-final-<id>.html` 이 하나씩 있고 앱이 그것을 '정답·개념 해설' 이라는
이름으로 링크한다. 그런데 담긴 내용이 회차마다 다르다.

    JMChC 1~14 · KMChC 옛 연도   문항별 풀이까지 있다
    기출동형 4회 · 일부 KMChC 2024~2026             정답·영역·개념표까지만 있다

이름은 하나인데 내용이 다르면, 해설을 기대하고 연 사람이 표만 보게 된다.
`solFull` 은 "그 회차에 문항별 풀이가 있는가"를 적어 둔 것이고, 앱은 이 값으로
링크 이름을 바꾼다 — 있는 것만 있다고 말하게 하는 장치다.

무엇을 보고 정하는가
--------------------
`answers/<id>.json` 의 문항 중 **하나라도** explanation 이나 explanationHtml 이
채워져 있으면 true. 해설을 새로 쓰면 이 값이 저절로 따라온다.

사용:
    python3 tools/gen_exam_solflag.py            # 어긋나면 1
    python3 tools/gen_exam_solflag.py --write    # exams.json 에 써 넣는다

    고친 뒤에는 `python3 tools/gen_exam_fallback.py --write` 도 함께 돌려야
    final.html 안의 예비본이 같이 맞는다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMS = ROOT / "exams.json"


def has_explanations(exam_id: str) -> bool:
    path = ROOT / "answers" / f"{exam_id}.json"
    if not path.exists():
        return False
    questions = json.loads(path.read_text(encoding="utf-8")).get("questions") or {}
    values = questions.values() if isinstance(questions, dict) else questions
    for q in values:
        if not isinstance(q, dict):
            continue
        if str(q.get("explanation") or "").strip() or str(q.get("explanationHtml") or "").strip():
            return True
    return False


def render(exams: list[dict]) -> str:
    """회차 하나에 한 줄. 파일이 원래 그렇게 쓰여 있다 — 통째로 다시 들여쓰면
    한 필드를 고쳐도 7천 줄이 바뀐 것처럼 보여 나중에 뭘 고쳤는지 못 읽는다."""
    lines = [json.dumps(e, ensure_ascii=False, separators=(",", ":")) for e in exams]
    return "[\n " + ",\n ".join(lines) + "\n]\n"


def main() -> int:
    exams = json.loads(EXAMS.read_text(encoding="utf-8"))
    changed, full = [], []
    for exam in exams:
        want = has_explanations(exam["id"])
        if want:
            full.append(exam["id"])
        if bool(exam.get("solFull")) != want:
            changed.append(f"{exam['id']}: {exam.get('solFull')!r} → {want}")
        exam["solFull"] = want

    print(f"문항별 해설이 있는 회차 {len(full)}/{len(exams)}개")
    thin = [e["id"] for e in exams if not e["solFull"]]
    if thin:
        print(f"  정답·개념표까지만: {', '.join(thin)}")

    if "--write" in sys.argv[1:]:
        EXAMS.write_text(render(exams), encoding="utf-8")
        print(f"\nexams.json 에 적었다 ({len(changed)}개 회차 변경)")
        return 0
    if changed:
        print("\nFAIL solFull 이 해설 데이터와 어긋난다. --write 로 갱신한다:")
        for c in changed[:10]:
            print("  " + c)
        return 1
    print("\nPASS 파일과 일치")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
