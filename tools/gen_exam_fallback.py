#!/usr/bin/env python3
"""`exams.json` 을 `final.html`·`final-submit.html` 안에 예비본으로 심는다.

시험 목록을 exams.json 한 곳으로 뺐더니 **그 파일 하나가 늦게 오면 앱 전체가
죽는** 문제가 생겼다. 실제로 배포 직후 CDN 전파 시차 때문에 성적표 링크로 들어온
학생이 "시험 목록을 불러오지 못했습니다 · HTTP 404"만 보고 끝났다. 분리하기
전에는 final.html 이 자체 완결이라 이런 일이 없었다.

그래서 예비본을 파일 안에 다시 넣는다. 다만 **손으로 관리하는 사본이 아니다.**
- 고치는 곳은 언제나 exams.json 하나다(한 줄에 시험 하나라 diff 도 읽힌다)
- 이 도구가 그것을 그대로 심고, CI 가 `--check` 로 두 벌이 같은지 매번 본다
- 사람이 예비본을 직접 고칠 일은 없고, 고쳐도 CI 가 잡는다

앱은 exams.json 을 먼저 받아 보고(그게 최신이다), 못 받으면 예비본으로 조용히
이어 간다. 학생 화면에는 아무 일도 일어나지 않는다.

사용:
    python3 tools/gen_exam_fallback.py            # 심을 내용 요약
    python3 tools/gen_exam_fallback.py --write    # 두 파일에 심는다
    python3 tools/gen_exam_fallback.py --check    # 어긋나면 종료 코드 1 (CI용)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("final.html", "final-submit.html")
MARK = "const FALLBACK_EXAMS="


def payload() -> str:
    exams = json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))
    return MARK + json.dumps(exams, ensure_ascii=False, separators=(",", ":")) + ";"


def current(text: str) -> str | None:
    at = text.find(MARK)
    if at < 0:
        return None
    end = text.index(";\n", at)
    return text[at:end + 1]


def main() -> int:
    want = payload()
    args = sys.argv[1:]
    bad = []
    for name in TARGETS:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        have = current(text)
        if have is None:
            bad.append(f"{name}: FALLBACK_EXAMS 자리가 없다")
            continue
        if have == want:
            continue
        if "--write" in args:
            path.write_text(text.replace(have, want, 1), encoding="utf-8")
            print(f"{name} 예비본 갱신")
        else:
            bad.append(f"{name}: exams.json 과 어긋난다")

    n = len(json.loads((ROOT / "exams.json").read_text(encoding="utf-8")))
    if bad and "--write" not in args:
        for line in bad:
            print("FAIL " + line)
        print("     python3 tools/gen_exam_fallback.py --write 로 맞춘다")
        return 1
    print(f"PASS 예비본이 exams.json 과 일치 (시험 {n}개, {len(want)/1024:.0f}KB)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
