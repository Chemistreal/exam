#!/usr/bin/env python3
"""동형문제 상시 검사. 사람이 볼 수 없는 규모(2400문항)를 기계가 매번 훑는다.

집필이 끝난 뒤에도 파일은 계속 손을 탄다. 한 문항을 고치다 표기가 되돌아가거나,
정답을 바꾸다 한 선택지에 답이 몰리는 일은 눈으로는 잡히지 않는다. 여기서 보는
것은 '사람이 매번 확인할 수 없는 것'뿐이고, 화학 내용의 옳고 그름은 보지 않는다.

검사 항목

1. 표기 잔여 — `dh_normalize.py` 를 읽기 전용으로 돌려 **고칠 것이 하나도 없어야**
   한다. ASCII 화학식(H2O)·화살표(->)·도씨·반쪽 지수(10¹.77)·위첨자 뒤 ASCII
   부호·아래첨자로 내려간 전하(Cu₂+)가 다시 들어오면 여기서 걸린다.
   정규화기 자체가 세 번 틀렸던 자리라(README 규칙 9) 결과를 그대로 믿지 않고,
   '바뀔 것이 있는가'만 본다. 실제 치환은 사람이 확인하고 `--write` 로 한다.

2. 정답 분포 — 한 시험 안에서 한 선택지에 답이 몰리면 학생이 찍어서 뚫는다.
   지금은 어느 시험도 28%를 넘지 않는다. 32%를 넘거나 15% 아래로 떨어지면 걸린다.
   (60문항 기준 32% = 20개, 15% = 9개. 균등이면 25% = 15개다.)

3. 문항 형식 — 정답이 1~4 밖이거나 비어 있는 것, 선택지가 4개가 아닌 것,
   `dhUsable()`(final.html) 이 화면에서 숨겨 버릴 손상 문항.

사용:
    python3 tools/dh_lint.py          # 어긋나면 종료 코드 1
    python3 tools/dh_lint.py -v       # 통과한 항목까지 모두 출력
"""

from __future__ import annotations

import collections
import glob
import json
import re
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dh_normalize  # noqa: E402  (같은 폴더의 정규화 규칙을 그대로 쓴다)

ROOT = Path(__file__).resolve().parents[1]

# 한 선택지에 답이 이보다 많이/적게 몰리면 걸린다. 균등은 25%.
MAX_SHARE = 0.32
MIN_SHARE = 0.15
# 문항 수가 이보다 적으면 분포를 따지지 않는다(표본이 작아 흔들리는 게 정상).
MIN_N_FOR_SHARE = 20

# final.html 의 dhUsable() 과 같은 판정. 저쪽이 바뀌면 여기도 같이 고친다.
BROKEN = re.compile(
    r"(?:렌더|렌더링|추출|복원|원본)[^\n]{0,30}?누락"
    r"|누락[^\n]{0,30}?(?:렌더|렌더링|추출|복원)"
    r"|렌더\s*실패|추출\s*실패|복원되지\s*않"
)

FIELDS = ("stem", "explanation", "misconception")


def authored() -> list[tuple[str, dict]]:
    out = []
    for path in sorted(glob.glob(str(ROOT / "donghyung" / "*.json"))):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("strategy") == "original-authored":
            out.append((Path(path).stem, data))
    return out


def notation_residue(data: dict) -> list[str]:
    """정규화기가 바꾸려 드는 자리를 모은다. 비어 있어야 정상."""
    hits = []
    for qno, question in data["questions"].items():
        texts = [(f, question.get(f)) for f in FIELDS]
        for key in ("choices", "misconceptions"):
            value = question.get(key)
            if isinstance(value, list):
                texts += [(f"{key}[{i}]", v) for i, v in enumerate(value)]
            elif isinstance(value, dict):
                texts += [(f"{key}[{k}]", v) for k, v in value.items()]
        for field, value in texts:
            if not isinstance(value, str):
                continue
            fixed = dh_normalize.normalize(value)
            if fixed != value:
                for old, new in dh_normalize.diff_tokens(value, fixed):
                    hits.append(f"{qno}번 {field}: {old} → {new}")
    return hits


def shape_errors(data: dict) -> list[str]:
    out = []
    for qno, q in data["questions"].items():
        answer = q.get("answer")
        if not isinstance(answer, int) or not 1 <= answer <= 4:
            out.append(f"{qno}번 정답이 1~4 가 아님: {answer!r}")
        choices = q.get("choices") or q.get("choicesHtml") or []
        if len(choices) != 4:
            out.append(f"{qno}번 선택지가 {len(choices)}개")
        stem = str(q.get("stem") or q.get("stemHtml") or "")
        if not stem.strip() and not q.get("image"):
            out.append(f"{qno}번 지문과 이미지가 모두 없음")
        blob = stem + str(q.get("explanation") or q.get("explanationHtml") or "")
        if BROKEN.search(blob):
            out.append(f"{qno}번 손상 문항(dhUsable 이 화면에서 숨김)")
    return out


def answer_share(data: dict) -> tuple[list[str], list[int], int]:
    count = collections.Counter(q.get("answer") for q in data["questions"].values())
    dist = [count[i] for i in (1, 2, 3, 4)]
    n = sum(dist)
    if n < MIN_N_FOR_SHARE:
        return [], dist, n
    out = []
    for i, c in enumerate(dist, 1):
        share = c / n
        if share > MAX_SHARE:
            out.append(f"{i}번 답이 {c}/{n} = {share*100:.0f}% (한도 {MAX_SHARE*100:.0f}%)")
        elif share < MIN_SHARE:
            out.append(f"{i}번 답이 {c}/{n} = {share*100:.0f}% (하한 {MIN_SHARE*100:.0f}%)")
    return out, dist, n


def main() -> int:
    verbose = "-v" in sys.argv[1:]
    exams = authored()
    if not exams:
        print("FAIL 재집필된 동형문제 파일을 찾지 못했다")
        return 1

    problems: list[str] = []
    total_q = 0
    global_dist = [0, 0, 0, 0]
    worst = (0.0, "", [])

    for exam_id, data in exams:
        n_q = len(data["questions"])
        total_q += n_q
        lines = []
        lines += [f"표기 잔여 · {h}" for h in notation_residue(data)]
        lines += [f"문항 형식 · {h}" for h in shape_errors(data)]
        share_bad, dist, n = answer_share(data)
        lines += [f"정답 분포 · {h}" for h in share_bad]
        for i in range(4):
            global_dist[i] += dist[i]
        if n:
            top = max(dist) / n
            if top > worst[0]:
                worst = (top, exam_id, dist)
        if lines:
            problems.append(exam_id)
            print(f"FAIL {exam_id}")
            for line in lines[:20]:
                print(f"       {line}")
            if len(lines) > 20:
                print(f"       … 외 {len(lines)-20}건")
        elif verbose:
            print(f"  ok  {exam_id}  ({n_q}문항, 정답 분포 {dist})")

    # ── 저장소 전체 온도 표기 ────────────────────────────
    # 위 검사는 재집필한 동형문제만 본다. 그런데 ℃(U+2103)는 해설·답안 자료
    # 곳곳에 3,666군데 있었고, **한 화면 안에서 두 표기가 섞여** 있었다
    # (grade-j0.html: ℃ 11개 · °C 10개). 그 글자는 CJK 호환용이라 유니코드가
    # 쓰지 말라고 권하고, "°C" 로 찾으면 안 걸린다. °C 로 모았으니 지킨다.
    root = ROOT if "ROOT" in dir() else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stray = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__")]
        for fn in filenames:
            if not fn.endswith((".json", ".html")):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                text = open(fp, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            n = text.count("\u2103")
            if n:
                stray.append(f"{os.path.relpath(fp, root)} ({n}곳)")
    if stray:
        problems.append("온도 표기")
        print("FAIL 온도 표기가 ℃ 로 남아 있다 (°C 로 모은다)")
        for line in stray[:10]:
            print(f"       {line}")
        if len(stray) > 10:
            print(f"       … 외 {len(stray)-10}개 파일")

    gt = sum(global_dist)
    print(
        f"\n{'FAIL' if problems else 'PASS'} dh_lint: 시험 {len(exams)}개 · 문항 {total_q}개 · "
        f"전체 정답 분포 {global_dist} "
        f"(최대 {max(global_dist)/gt*100:.1f}%) · "
        f"한 시험 최대 쏠림 {worst[0]*100:.0f}% ({worst[1]} {worst[2]})"
    )
    if problems:
        print(f"     걸린 시험: {', '.join(problems)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
