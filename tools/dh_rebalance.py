#!/usr/bin/env python3
"""한 번호에 몰린 정답을 고르게 흩는다.

집필 지시에 "정답을 1~4에 고르게 나누라"를 넣기 전에 쓴 초기 시험은 답이 한쪽에
몰려 있다. jmchc-1 은 60문항 중 31개(52 %)가 ②번이었다. ②만 찍어도 절반을
맞히면 오답노트가 진단 도구로서 값을 잃는다.

**선택지를 통째로 맞바꾸는 방식만 쓴다.** 정답 위치 a 를 목표 위치 t 로 옮길 때
choices[a] 와 choices[t] 를 교환하고, `misconceptions` 에서 t 를 빼고 a 에
원래 t 의 설명을 넣는다. 지문·해설·정답 내용은 손대지 않으므로 화학이 바뀌지
않는다.

**해설이 "→ ②" 처럼 선택지 번호를 가리키면 건드리지 않는다.** 번호를 바꾸면
해설이 어긋나기 때문이다. 그런 문항은 건너뛰고 목록으로 보여 주니 사람이
직접 고친다.

사용:
    python3 tools/dh_rebalance.py <examId>            # 바뀔 내용만 보여 준다
    python3 tools/dh_rebalance.py <examId> --write    # 실제로 고친다
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CIRCLED = re.compile(r"[①②③④]")


def plan(questions: dict) -> tuple[dict[str, int], list[str]]:
    """문항별 목표 정답 위치와, 손댈 수 없는 문항 번호를 돌려준다."""
    locked = [
        k for k, v in questions.items() if CIRCLED.search(v.get("explanation", ""))
    ]
    movable = [k for k in sorted(questions, key=int) if k not in locked]

    counts = collections.Counter(v["answer"] for v in questions.values())
    # 손댈 수 없는 문항의 답은 이미 확정이므로 목표 계산에서 미리 뺀다.
    fixed = collections.Counter(questions[k]["answer"] for k in locked)
    target_total = len(questions)
    quota = {i: target_total // 4 + (1 if i <= target_total % 4 else 0) for i in range(1, 5)}
    remaining = {i: max(0, quota[i] - fixed[i]) for i in range(1, 5)}

    # 원래 답을 그대로 둘 수 있으면 두는 쪽이 낫다. 남은 자리가 있는 번호부터
    # 채우되, 이미 그 번호인 문항을 우선 배정한다.
    assignment: dict[str, int] = {}
    for key in movable:
        current = questions[key]["answer"]
        if remaining[current] > 0:
            assignment[key] = current
            remaining[current] -= 1
    for key in movable:
        if key in assignment:
            continue
        target = max(remaining, key=lambda i: remaining[i])
        assignment[key] = target
        remaining[target] -= 1
    return assignment, locked


def apply_swap(question: dict, target: int) -> None:
    current = question["answer"]
    if current == target:
        return
    choices = question["choices"]
    choices[current - 1], choices[target - 1] = choices[target - 1], choices[current - 1]
    misconceptions = dict(question.get("misconceptions") or {})
    moved = misconceptions.pop(str(target), "")
    misconceptions[str(current)] = moved
    question["misconceptions"] = {
        k: misconceptions[k] for k in sorted(misconceptions, key=int)
    }
    question["answer"] = target


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        raise SystemExit(1)
    exam_id = args[0]
    write = "--write" in args

    path = ROOT / "donghyung" / f"{exam_id}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data["questions"]

    before = collections.Counter(v["answer"] for v in questions.values())
    assignment, locked = plan(questions)
    moved = [(k, questions[k]["answer"], t) for k, t in assignment.items() if questions[k]["answer"] != t]

    for key, target in assignment.items():
        apply_swap(questions[key], target)

    after = collections.Counter(v["answer"] for v in questions.values())
    print(f"[{exam_id}] {len(questions)}문항")
    print(f"  전 {[before[i] for i in range(1, 5)]}  →  후 {[after[i] for i in range(1, 5)]}")
    print(f"  옮긴 문항 {len(moved)}개")
    if locked:
        print(f"  해설이 선택지 번호를 가리켜 건드리지 않은 문항: {', '.join(locked)}")
    for key, old, new in moved[:12]:
        print(f"    {key:>2}번 {old} → {new}")
    if len(moved) > 12:
        print(f"    … 그 밖 {len(moved) - 12}개")

    if write:
        indent = 1 if path.read_text(encoding="utf-8").startswith("{\n ") else 2
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8"
        )
        print("  저장했다.")
    else:
        print("  (미리 보기. 실제로 고치려면 --write)")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # `| head` 로 잘라 볼 때 역추적을 남기지 않는다
        pass
