#!/usr/bin/env python3
"""성적표 엑셀(.xlsm)에서 **익명 점수 분포**만 뽑아 `cohort/baseline.json` 을 만든다.

왜 필요한가
-----------
석차·백분위는 그때까지 이 브라우저에 채점해 둔 학생 수를 모집단으로 삼았다.
그래서 같은 시험인데 학생마다 인원이 달랐다 — 먼저 채점한 학생은 `3/9`,
나중에 채점한 학생은 `8/10`, 8명이 되기 전에 본 학생은 아예 석차가 없었다.
모집단이 "지금까지 내가 채점한 만큼"이면 석차는 뜻을 잃는다.

시험지 한 회차를 실제로 응시한 사람은 성적표 엑셀에 다 들어 있다. 그것을
모집단으로 쓰면 누구를 먼저 채점하든 같은 숫자가 나온다.

무엇을 담고, 무엇을 안 담는가
-----------------------------
**이름·학교·학년·수험번호는 담지 않는다.** 이 저장소는 공개되어 있다.
담는 것은 회차별 점수 히스토그램뿐이다 — "몇 점을 몇 명이 받았는가".
그것만으로 석차와 백분위가 나온다. 엑셀 원본은 저장소에 넣지 않는다.

총점은 180점 만점(문항당 3점)이라 3으로 나누면 맞은 문항 수가 된다.
3의 배수가 아닌 값이 있으면 감점이 섞였다는 뜻이므로 세지 않고 알린다.

사용:
    python3 tools/gen_cohort_baseline.py <엑셀들이 있는 디렉터리> [--write]

    같은 회차 파일이 여럿이면(11회 0804 · 0811 처럼) 사람이 많은 쪽을 쓴다.
    나중에 받은 파일이 대개 몇 명 더 들어와 있다.
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cohort" / "baseline.json"

SHEET = "성적입력"
NAME_COL, TOTAL_COL = 1, 6      # 0-based: 성명 · 총점
FIRST_ROW = 7                   # 6행이 머리글
PER_Q = 3                       # 문항당 배점


def rounds(folder: Path) -> dict[str, tuple[Path, list[int]]]:
    """회차 id → (파일, 맞은 문항 수 목록). 같은 회차는 사람이 많은 파일을 남긴다."""
    try:
        import openpyxl
    except ImportError:
        print("openpyxl 이 필요하다:  pip install openpyxl", file=sys.stderr)
        raise SystemExit(2)

    best: dict[str, tuple[Path, list[int]]] = {}
    odd: list[str] = []
    for path in sorted(folder.rglob("*.xls*")):
        found = re.search(r"JMchC\s+([\d-]+)\s*[#사]", path.name, re.IGNORECASE)
        if not found:
            print(f"  건너뜀(회차를 못 읽음) {path.name}")
            continue
        exam_id = "jmchc-" + found.group(1)
        book = openpyxl.load_workbook(path, data_only=True, read_only=True)
        if SHEET not in book.sheetnames:
            print(f"  건너뜀('{SHEET}' 시트 없음) {path.name}")
            continue
        scores = []
        for row in book[SHEET].iter_rows(min_row=FIRST_ROW, max_col=TOTAL_COL + 1, values_only=True):
            name, total = row[NAME_COL], row[TOTAL_COL]
            if not name or not isinstance(total, (int, float)):
                continue
            total = int(total)
            if total % PER_Q or total < 0:
                odd.append(f"{path.name} {total}점")
                continue
            scores.append(total // PER_Q)
        if not scores:
            continue
        if exam_id not in best or len(scores) > len(best[exam_id][1]):
            best[exam_id] = (path, scores)
    if odd:
        print(f"  ! 3의 배수가 아닌 총점 {len(odd)}건은 세지 않았다: {', '.join(odd[:5])}")
    return best


def build(folder: Path) -> dict:
    picked = rounds(folder)
    exams = {}
    for exam_id, (path, scores) in picked.items():
        hist = collections.Counter(scores)
        exams[exam_id] = {
            "n": len(scores),
            "hist": {str(k): hist[k] for k in sorted(hist)},
        }
        print(f"  {exam_id:12s} {len(scores):3d}명  평균 {sum(scores)/len(scores):4.1f}"
              f"  범위 {min(scores)}~{max(scores)}   ← {path.name}")
    return {
        "note": "회차별 점수 히스토그램(맞은 문항 수 → 사람 수). 이름·학교는 담지 않는다.",
        "source": "조준모의고사 성적표 엑셀의 '성적입력' 시트",
        "exams": dict(sorted(exams.items(), key=lambda kv: _order(kv[0]))),
    }


def _order(exam_id: str) -> tuple[int, int]:
    nums = re.findall(r"\d+", exam_id)
    return (int(nums[0]) if nums else 0, int(nums[1]) if len(nums) > 1 else 0)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    folder = Path(args[0]).expanduser()
    if not folder.is_dir():
        print(f"디렉터리가 아니다: {folder}", file=sys.stderr)
        return 2
    data = build(folder)
    total = sum(e["n"] for e in data["exams"].values())
    print(f"\n{len(data['exams'])}개 회차 · {total}명")

    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if "--write" in sys.argv[1:]:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
        print(f"{OUT.relative_to(ROOT)} 에 적었다 ({len(text)/1024:.1f}KB)")
        return 0
    print("\n--write 를 붙이면 파일에 적는다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
